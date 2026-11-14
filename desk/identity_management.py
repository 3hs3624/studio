"""Audited user/profile, role, group and security policy administration."""
import ipaddress, uuid
from datetime import date,timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.utils import timezone
from . import services as s
from .permissions import PERMISSIONS, BUILTIN, effective, require
from .security_policy import require_recent, policy, state, validate, password_check, change_password, allowed_ip, FIELDS
from .models import (Person,UserProfile,PrivacyAccessEvent,RoleDefinition,CustomRoleGrant,Group,Membership,
                     Ticket,SecurityPolicy,RoleGrant,LoginSession)


def person(actor,id):
    value=Person.objects.filter(id=s.identifier(id),organization=actor.organization).select_related('user','profile').first()
    if not value:s.fail('NOT_FOUND','사용자를 찾을 수 없습니다.',404)
    return value


def role(actor,id):
    value=RoleDefinition.objects.filter(id=s.identifier(id),organization=actor.organization).first()
    if not value:s.fail('NOT_FOUND','역할을 찾을 수 없습니다.',404)
    return value


def group(actor,id):
    value=Group.objects.filter(id=s.identifier(id),organization=actor.organization).first()
    if not value:s.fail('NOT_FOUND','그룹을 찾을 수 없습니다.',404)
    return value


def authorize(actor,operation,target):
    if operation.startswith('manage_org_'):
        require(actor,'iam.manage');require_recent(actor);return
    if operation not in {'manage_user_create','manage_user_save','manage_user_reset','manage_user_invite','manage_user_unlock','manage_user_mfa_reset','manage_user_session','manage_user_erase','manage_role_save','manage_role_grant','manage_role_delete','manage_group_save','manage_group_delete','manage_policy_save','manage_policy_preview'}:s.fail('INVALID_OPERATION','허용되지 않은 작업입니다.')
    category=operation.split('_')[1]
    require(actor,'security.manage' if category=='policy' else 'users.manage' if category=='user' else 'iam.manage')
    require_recent(actor)
    if target and category!='policy':
        value={'user':person,'role':role,'group':group}[category](actor,target)
        if category=='user' and RoleGrant.objects.filter(person=value,role='ORG_ADMIN').exists() and not RoleGrant.objects.filter(person=actor,role='ORG_ADMIN').exists():s.fail('PRIVILEGED_ACCOUNT','시스템 관리자 계정은 시스템 관리자만 변경할 수 있습니다.',403)


def code(data):
    import re
    value=s.text(data,'code',40).upper()
    if not re.fullmatch(r'[A-Z][A-Z0-9_]{0,39}',value):s.fail('INVALID_CODE','영문 대문자·숫자·밑줄 코드를 입력하십시오.')
    return value


def profile_values(data):
    result={}
    for key,maxlength in [('full_name',200),('given_name',150),('family_name',150),('email',254),('phone',40),('employee_id',80)]:
        if key in data:result[key]=s.text(data,key,maxlength,required=key=='full_name')
    if result.get('email'):
        try:validate_email(result['email'])
        except ValidationError:s.fail('INVALID_INPUT','이메일 형식을 확인하십시오.')
    return result


def finish(actor,obj,action,request_id,reason,extra=None):
    metadata={'code':obj.code,'name':obj.name} if isinstance(obj,(RoleDefinition,Group)) else {}
    s.record(actor,obj,action,request_id,after={'reason':reason,**metadata,**(extra or {})})
    return dict(id=str(obj.id),version=obj.row_version if hasattr(obj,'row_version') else 1),200


def mutate(actor,operation,data,request_id,target):
    if operation.startswith('manage_org_'):
        from .organization_management import mutate as organization_mutate
        return organization_mutate(actor,operation,data,request_id,target)
    reason=s.text(data,'reason',500)
    if operation=='manage_role_save':
        s.check_fields(data,['code','name','description','permissions','active','expected_version','reason'],['code','name','description','permissions','active','expected_version','reason'])
        value=role(actor,target) if target else None
        key=code(data)
        if key in BUILTIN or (value and value.system):s.fail('SYSTEM_ROLE','기본 시스템 역할은 변경할 수 없습니다.',409)
        permissions=data['permissions']
        if not isinstance(permissions,list) or any(not isinstance(p,str) or p not in PERMISSIONS for p in permissions) or len(set(permissions))!=len(permissions):s.fail('INVALID_PERMISSIONS','허용된 권한을 중복 없이 선택하십시오.')
        if not RoleGrant.objects.filter(person=actor,role='ORG_ADMIN').exists() and not set(permissions)<=effective(actor):s.fail('CANNOT_DELEGATE','자신에게 없는 권한을 위임할 수 없습니다.',403)
        if any(p.startswith(('entity.','plugin.','code.')) or p in ('users.manage','iam.manage','security.manage') for p in permissions) and 'console.access' not in permissions:s.fail('INVALID_PERMISSIONS','관리 기능에는 운영 콘솔 접근 권한도 필요합니다.')
        if type(data['active']) is not bool:s.fail('INVALID_INPUT','사용 여부를 확인하십시오.')
        if value:
            s.version(value,data)
            if key!=value.code:s.fail('IMMUTABLE_CODE','역할 코드는 변경할 수 없습니다.')
        else:
            if data['expected_version']!=0:s.fail('VERSION_CONFLICT','새 역할의 버전은 0입니다.',409)
            if RoleDefinition.objects.filter(organization=actor.organization,code=key).exists():s.fail('ROLE_EXISTS','이미 존재하는 역할입니다.',409)
            value=RoleDefinition(organization=actor.organization,code=key,row_version=0)
        value.name=s.text(data,'name',100);value.description=s.text(data,'description',500,False)
        value.permissions=permissions;value.active=data['active'];value.row_version+=1;value.save()
        return finish(actor,value,'ROLE_DEFINED',request_id,reason,{'permissions':permissions,'active':value.active})
    if operation=='manage_role_grant':
        s.check_fields(data,['person_id','active','expected_version','reason'],['person_id','active','expected_version','reason'])
        value=role(actor,target);s.version(value,data)
        if value.system or (not RoleGrant.objects.filter(person=actor,role='ORG_ADMIN').exists() and not set(value.permissions)<=effective(actor)):s.fail('CANNOT_DELEGATE','이 역할을 배정할 수 없습니다.',403)
        member=person(actor,data['person_id'])
        if type(data['active']) is not bool or (data['active'] and (not value.active or not member.active)):s.fail('INVALID_INPUT','활성 역할·사용자를 선택하십시오.')
        CustomRoleGrant.objects.update_or_create(organization=actor.organization,role=value,person=member,defaults={'active':data['active']})
        member.session_epoch=uuid.uuid4();s.bump(member);s.bump(value)
        return finish(actor,value,'CUSTOM_ROLE_ASSIGNED',request_id,reason,{'person_id':str(member.id),'active':data['active']})
    if operation in ('manage_role_delete','manage_group_delete'):
        s.check_fields(data,['expected_version','reason'],['expected_version','reason'])
        value=role(actor,target) if operation=='manage_role_delete' else group(actor,target);s.version(value,data)
        from .models import ScopedRoleGrant,RoleMenuPolicy,GroupDepartment
        if operation=='manage_role_delete' and (value.system or CustomRoleGrant.objects.filter(role=value).exists() or ScopedRoleGrant.objects.filter(role=value).exists() or RoleMenuPolicy.objects.filter(role=value).exists()):s.fail('IN_USE','사용 이력이 있는 역할은 삭제 대신 사용 중지하십시오.',409)
        if operation=='manage_group_delete' and (value.triage or Membership.objects.filter(group=value).exists() or GroupDepartment.objects.filter(group=value).exists() or ScopedRoleGrant.objects.filter(group=value).exists()):s.fail('IN_USE','접수 그룹 또는 구성원이 있는 그룹은 삭제할 수 없습니다.',409)
        result=finish(actor,value,'ROLE_DELETED' if operation=='manage_role_delete' else 'GROUP_DELETED',request_id,reason)
        try:value.delete()
        except ProtectedError:s.fail('IN_USE','업무 이력이 있는 그룹은 삭제 대신 사용 중지하십시오.',409)
        return result
    if operation=='manage_group_save':
        s.check_fields(data,['code','name','description','active','expected_version','reason'],['code','name','description','active','expected_version','reason'])
        value=group(actor,target) if target else None;key=code(data)
        if type(data['active']) is not bool:s.fail('INVALID_INPUT','사용 여부를 확인하십시오.')
        if value:
            s.version(value,data)
            if key!=value.code:s.fail('IMMUTABLE_CODE','그룹 코드는 변경할 수 없습니다.')
            if not data['active'] and (value.triage or Ticket.objects.filter(group=value).exclude(status__in=['CLOSED','REJECTED','CANCELLED']).exists()):s.fail('OPEN_ASSIGNMENTS','접수 그룹은 유지하고 진행 업무는 먼저 이관하십시오.',409)
        else:
            if data['expected_version']!=0:s.fail('VERSION_CONFLICT','새 그룹의 버전은 0입니다.',409)
            value=Group(organization=actor.organization,code=key,row_version=0)
        if Group.objects.filter(organization=actor.organization).filter(Q(code=key)|Q(name=data['name'])).exclude(id=value.id).exists():s.fail('GROUP_EXISTS','동일한 코드 또는 이름의 그룹이 있습니다.',409)
        value.name=s.text(data,'name',200);value.description=s.text(data,'description',500,False)
        value.active=data['active'];value.row_version+=1;value.save()
        return finish(actor,value,'GROUP_DEFINED',request_id,reason,{'active':value.active})
    if operation in ('manage_policy_save','manage_policy_preview'):
        s.check_fields(data,['configuration','expected_version','reason','apply_confirmed'],['configuration','expected_version','reason'])
        configuration=validate(target,data['configuration'])
        value=SecurityPolicy.objects.filter(organization=actor.organization,category=target).first()
        if data['expected_version']!=(value.row_version if value else 0):s.fail('VERSION_CONFLICT','정책이 변경되었습니다.',409)
        if target=='access':
            if configuration['admin_mfa_required'] and not state(actor).mfa_secret:s.fail('MFA_SETUP_REQUIRED','먼저 내 계정 보안에서 MFA를 등록하십시오.',409)
            if configuration['admin_allowed_cidrs']:
                if getattr(actor,'_proxy_unverified',False):s.fail('PROXY_CONFIGURATION_REQUIRED','서버의 신뢰 프록시 CIDR을 먼저 설정하십시오.',409)
                if not getattr(actor,'_request_context',None) or not allowed_ip(actor,actor._request_context,configuration):s.fail('SELF_LOCKOUT','현재 관리자 접속 IP가 허용 범위에 포함되어야 합니다.',409)
        if operation=='manage_policy_preview':
            current=policy(actor.organization,target)
            changes=[f'{FIELDS[target][key][3]}: {str(current[key])[:120]} → {str(val)[:120]}' for key,val in configuration.items() if current[key]!=val]
            return {'output':{'text':f'검증 완료 · 적용 대상 {Person.objects.filter(organization=actor.organization).count()}명\n'+('\n'.join(changes) or '변경 항목 없음')+'\n적용 후 다음 로그인/요청부터 검사합니다.'}},200
        if data.get('apply_confirmed') is not True:s.fail('CONFIRMATION_REQUIRED','영향 범위를 확인하고 즉시 적용을 선택하십시오.')
        if not value:value=SecurityPolicy(organization=actor.organization,category=target,row_version=0,applied_by=actor)
        before=value.configuration;value.configuration=configuration;value.row_version+=1
        value.applied_by=actor;value.applied_at=timezone.now();value.save()
        s.record(actor,value,'SECURITY_POLICY_APPLIED',request_id,before=before,after={'configuration':configuration,'reason':reason,'version':value.row_version})
        return dict(id=str(value.id),version=value.row_version),200
    member=person(actor,target) if target else None
    if operation=='manage_user_create':
        s.check_fields(data,['username','full_name','email','phone','employee_id','password','invite','reason','department_id','allocation_token','role_keys','group_ids'],['username','full_name','invite','reason'])
        username=s.text(data,'username',150);User=get_user_model()
        try:User._meta.get_field('username').run_validators(username)
        except ValidationError:s.fail('INVALID_INPUT','로그인 ID 형식을 확인하십시오.')
        if type(data['invite']) is not bool:s.fail('INVALID_INPUT','초대 여부를 확인하십시오.')
        if User.objects.filter(username=username).exists():s.fail('USER_EXISTS','이미 사용 중인 로그인 ID입니다.',409)
        user=User.objects.create_user(username=username,password=None)
        member=Person.objects.create(organization=actor.organization,user=user,display_name=s.text(data,'full_name',200))
        values=profile_values(data);UserProfile.objects.filter(person=member).update(**values)
        days=policy(actor.organization,'account')['default_expiry_days']
        if days:member.expires_on=timezone.localdate()+timedelta(days=days);member.save(update_fields=['expires_on'])
        if not data['invite']:
            try:change_password(member,data.get('password',''),force=True)
            except ValidationError as exc:s.fail('INVALID_PASSWORD',' '.join(exc.messages))
        from .organization_management import apply_new_user
        allocations=apply_new_user(actor,member,data)
        return finish(actor,member,'USER_CREATED',request_id,reason,{'profile_fields':list(values),'invite':data['invite'],**allocations})
    s.version(member,data)
    if operation=='manage_user_save':
        allowed=['full_name','given_name','family_name','email','phone','employee_id','expires_on','department_id','expected_version','reason']
        s.check_fields(data,allowed,['full_name','expires_on','expected_version','reason'])
        try:expiry=date.fromisoformat(data['expires_on']) if data['expires_on'] else None
        except (TypeError,ValueError):s.fail('INVALID_INPUT','사용 종료일을 확인하십시오.')
        if expiry and RoleGrant.objects.filter(person=member,role='ORG_ADMIN').exists() and not RoleGrant.objects.filter(organization=actor.organization,role='ORG_ADMIN',person__active=True,person__user__is_active=True,person__expires_on__isnull=True).exclude(person=member).exists():s.fail('LAST_ADMIN','사용 종료일이 없는 다른 시스템 관리자를 먼저 확보하십시오.',409)
        if member.id==actor.id and expiry and expiry<timezone.localdate():s.fail('SELF_LOCKOUT','현재 관리자 계정을 만료시킬 수 없습니다.',409)
        values=profile_values(data);UserProfile.objects.filter(person=member).update(**values)
        if 'department_id' in data:
            from .organization_management import department,delegation
            member.department=department(actor,data['department_id']) if data['department_id'] else None
            from .access_graph import role_rows
            for assignment in role_rows(member):
                if assignment['key']!='EVERYONE':delegation(actor,assignment['key'])
        member.expires_on=expiry;s.bump(member)
        PrivacyAccessEvent.objects.create(organization=actor.organization,actor=actor,subject=member,action='UPDATE',request_id=request_id)
        return finish(actor,member,'USER_PROFILE_CHANGED',request_id,reason,{'profile_fields':list(values)})
    if operation=='manage_user_reset':
        s.check_fields(data,['password','expected_version','reason'],['password','expected_version','reason'])
        try:change_password(member,data['password'],force=True)
        except ValidationError as exc:s.fail('INVALID_PASSWORD',' '.join(exc.messages))
        return finish(actor,member,'PASSWORD_RESET',request_id,reason)
    if operation=='manage_user_unlock':
        s.check_fields(data,['expected_version','reason'],['expected_version','reason'])
        credential=state(member);credential.failed_count=0;credential.first_failed_at=None;credential.locked_until=None;credential.reactivated_at=timezone.now();credential.save();s.bump(member)
        return finish(actor,member,'ACCOUNT_UNLOCKED',request_id,reason)
    if operation=='manage_user_mfa_reset':
        s.check_fields(data,['expected_version','reason'],['expected_version','reason'])
        if member.id==actor.id:s.fail('SELF_LOCKOUT','내 MFA는 내 계정 보안에서 관리하십시오.',409)
        credential=state(member);credential.mfa_secret='';credential.recovery_hashes=[];credential.save()
        member.session_epoch=uuid.uuid4();s.bump(member)
        return finish(actor,member,'MFA_RESET',request_id,reason)
    if operation=='manage_user_invite':
        s.check_fields(data,['expected_version','reason'],['expected_version','reason'])
        if member.user.has_usable_password():s.fail('INVITATION_UNAVAILABLE','이미 비밀번호를 설정한 계정은 초대할 수 없습니다.',409)
        return finish(actor,member,'INVITATION_ISSUED',request_id,reason)
    if operation=='manage_user_session':
        s.check_fields(data,['session_id','expected_version','reason'],['session_id','expected_version','reason'])
        session=LoginSession.objects.filter(id=s.identifier(data['session_id']),person=member,organization=actor.organization).first()
        if not session:s.fail('NOT_FOUND','세션을 찾을 수 없습니다.',404)
        session.revoked=True;session.save(update_fields=['revoked']);s.bump(member)
        return finish(actor,member,'USER_SESSION_REVOKED',request_id,reason)
    if operation=='manage_user_erase':
        s.check_fields(data,['expected_version','reason'],['expected_version','reason'])
        if member.active or member.id==actor.id:s.fail('ACCOUNT_ACTIVE','개인정보 파기 전 계정을 중지하십시오.',409)
        UserProfile.objects.filter(person=member).update(full_name='삭제된 사용자',given_name='',family_name='',email='',phone='',employee_id='')
        member.user.username='deleted-'+member.id.hex;member.user.set_unusable_password();member.user.save(update_fields=['username','password'])
        member.session_epoch=uuid.uuid4();s.bump(member)
        PrivacyAccessEvent.objects.create(organization=actor.organization,actor=actor,subject=member,action='ERASE',request_id=request_id)
        return finish(actor,member,'USER_PROFILE_ERASED',request_id,reason)
    s.fail('INVALID_OPERATION','허용되지 않은 관리 작업입니다.')
