"""One-time provisioned local accounts, with generated credentials outside source."""
import json
import os
import secrets
import uuid
from pathlib import Path
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from desk.models import Organization,Person,Group,Membership,RoleGrant,SecurityEvent

class Command(BaseCommand):
    help='Initialize a new local-login installation; never resets existing accounts.'
    def add_arguments(self,parser):
        group=parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--credential-file')
        group.add_argument('--password-prefix')
    def handle(self,*args,**options):
        prefix=options.get('password_prefix')
        if prefix and (not prefix.replace('_','').isalnum() or not prefix.isupper()):
            raise CommandError('Use an uppercase environment variable prefix.')
        target=Path(options['credential_file']).expanduser().resolve() if options.get('credential_file') else None
        usernames=['temp-admin','temp-manager','temp-employee','temp-assets','temp-buyer']
        existing=Person.objects.filter(user__username__in=usernames).count()
        if existing==len(usernames) and (prefix or target.is_file()):
            self.stdout.write('Existing local accounts and credential file retained.')
            return
        if Organization.objects.exists() or (target and target.exists()):
            raise CommandError('Refusing to alter an existing installation or credential file.')
        if target:target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        passwords={}
        for username in usernames:
            value=os.environ.get(prefix+username.upper().replace('-','_')+'_PASSWORD','') if prefix else secrets.token_urlsafe(24)
            if not value:raise CommandError('A required local account password variable is missing; no accounts created.')
            validate_password(value)
            passwords[username]=value
        if len(set(passwords.values())) != len(usernames):raise CommandError('Local accounts require different passwords.')
        accounts=[]
        with transaction.atomic():
            org=Organization.objects.create(name='Studio 임시 접속 조직')
            group=Group.objects.create(organization=org,name='IT 서비스 데스크',triage=True)
            for username,name,roles in [
                ('temp-admin','조직 관리자',['ORG_ADMIN']),
                ('temp-manager','서비스 담당자',['SERVICE_MANAGER','AGENT','RESOURCE_READER']),
                ('temp-employee','요청 사용자',[]),
                ('temp-assets','자산·재고 담당자',['ASSET_MANAGER','STOCK_MANAGER','RESOURCE_READER']),
                ('temp-buyer','구매 담당자',['PROCUREMENT_MANAGER']),
            ]:
                password=passwords[username]
                validate_password(password)
                user=get_user_model().objects.create_user(username=username,password=password)
                person=Person.objects.create(organization=org,user=user,display_name=name)
                for role in roles:RoleGrant.objects.create(organization=org,person=person,role=role)
                if 'AGENT' in roles:Membership.objects.create(organization=org,group=group,person=person)
                SecurityEvent.objects.create(organization=org,person=person,action='LOCAL_ACCOUNT_CREATED',request_id=uuid.uuid4())
                accounts.append({'username':username,'password':password,'purpose':name})
            if target:
                fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
                try:
                    with os.fdopen(fd,'w') as f:json.dump({'authentication':'local','organization_id':str(org.id),'accounts':accounts},f,ensure_ascii=False,indent=2)
                except BaseException:
                    target.unlink(missing_ok=True)
                    raise
        self.stdout.write('Local accounts created; credentials remain in the private file or provider environment. No defaults or bypass enabled.')
