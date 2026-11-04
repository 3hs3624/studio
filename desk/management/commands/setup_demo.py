import getpass
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from desk.models import Organization, Person, Group, Membership, RoleGrant, Asset, ConfigurationItem, BusinessCalendar, SLAPolicy

class Command(BaseCommand):
    help = 'Create synthetic local demo accounts. Prompts for a password; never enables authentication bypass.'
    @transaction.atomic
    def handle(self,*args,**options):
        if not settings.DEBUG:
            raise CommandError('Demo data is allowed only with DEBUG=1 in a local environment.')
        if Organization.objects.exists():
            raise CommandError('Use a new local database; existing data will not be overwritten.')
        password=getpass.getpass('Choose a password for the synthetic local accounts: ')
        validate_password(password)
        org=Organization.objects.create(name='Studio 데모 조직')
        group=Group.objects.create(organization=org,name='IT 서비스 데스크',triage=True)
        configurations=[('employee','김요청',[]),('agent','박담당',['AGENT','RESOURCE_READER']),
                        ('manager','이서비스',['SERVICE_MANAGER','AGENT','RESOURCE_READER','ASSET_MANAGER','STOCK_MANAGER']),
                        ('assetadmin','최자산',['ASSET_MANAGER','RESOURCE_READER']),
                        ('buyer','구매담당',['PROCUREMENT_MANAGER']),
                        ('stockadmin','재고담당',['STOCK_MANAGER','ASSET_MANAGER','RESOURCE_READER']),
                        ('orgadmin','정관리',['ORG_ADMIN'])]
        for username,name,roles in configurations:
            user=get_user_model().objects.create_user(username=username,password=password)
            person=Person.objects.create(organization=org,user=user,display_name=name)
            for role in roles:
                RoleGrant.objects.create(organization=org,person=person,role=role)
            if 'AGENT' in roles:
                Membership.objects.create(organization=org,person=person,group=group)
        ConfigurationItem.objects.create(organization=org,ci_no='CI-001',name='사내 네트워크',type='NETWORK',portal_visible=True)
        calendar=BusinessCalendar.objects.create(organization=org,name='평일 업무시간',timezone='Asia/Seoul',
                    weekdays=[0,1,2,3,4],starts_at='09:00',ends_at='18:00',holidays=[])
        for priority,response,resolution in [(1,15,60),(2,30,240),(3,60,480),(4,120,1440),(5,240,2400)]:
            SLAPolicy.objects.create(organization=org,calendar=calendar,name=f'장애 P{priority}',priority=priority,
                    version=1,response_minutes=response,resolution_minutes=resolution)
        from desk.services import execute
        import uuid
        manager=Person.objects.get(organization=org,user__username='manager')
        execute(manager,'asset_create',{'asset_no':'PC-001','name':'업무용 노트북','manufacturer':'Demo',
            'model':'Business Laptop','serial_number':'DEMO-001','location':'서울 사무실','portal_visible':True,
            'reason':'합성 데모 자산 등록'},'setup-demo-asset',uuid.uuid4())
        execute(manager,'catalog_publish',{'code':'LAPTOP','name':'업무용 노트북 신청',
            'description':'업무에 필요한 노트북을 신청합니다. 지정 승인자의 승인 후 IT 담당자가 처리합니다.',
            'fulfillment_group_id':str(group.id),'approval_required':True,'approver_id':str(manager.id),
            'public_to_org':True,'audience_group_ids':[],'available':True,'expected_version':0,
            'fields':[{'key':'reason','label':'신청 사유','type':'textarea','required':True},
                      {'key':'device','label':'장비 유형','type':'choice','required':True,'options':['일반 업무용','개발 업무용']}]},
            'setup-demo-catalog',uuid.uuid4())
        buyer=Person.objects.get(organization=org,user__username='buyer')
        stock=Person.objects.get(organization=org,user__username='stockadmin')
        for code,name,location in [('MAIN','IT 중앙 창고','서울 본사 창고'),('REMOTE','서울 예비 창고','서울 분산 창고')]:
            execute(stock,'stock_room',{'code':code,'name':name,'location':location},'setup-room-'+code,uuid.uuid4())
        for code,name,tracking,manufacturer,model in [('CABLE','USB 케이블','BULK','',''),('NOTEBOOK','재고 노트북','SERIALIZED','Demo','Notebook 14')]:
            execute(stock,'stock_item',{'code':code,'name':name,'tracking':tracking,'manufacturer':manufacturer,'model':model},'setup-item-'+code,uuid.uuid4())
        supplier,_=execute(buyer,'buy_supplier',{'code':'DEMO-SUPPLIER','name':'데모 공급업체','contact':''},'setup-supplier',uuid.uuid4())
        from django.utils import timezone
        year=timezone.localdate().year
        execute(buyer,'buy_contract',{'code':'DEMO-CONTRACT','name':'데모 장비 구매 계약','supplier_id':supplier['id'],
            'starts_on':f'{year}-01-01','ends_on':f'{year+1}-12-31','currency':'KRW','amount':'100000000','notes':'합성 데이터'},'setup-contract',uuid.uuid4())
        self.stdout.write(self.style.SUCCESS('Created local accounts: employee, agent, manager, assetadmin, buyer, stockadmin, orgadmin. Use your chosen password.'))
