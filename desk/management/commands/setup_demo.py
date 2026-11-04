import getpass
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from desk.models import Organization, Person, Group, Membership, RoleGrant, Asset, ConfigurationItem

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
                        ('manager','이서비스',['SERVICE_MANAGER','AGENT','RESOURCE_READER']),
                        ('orgadmin','정관리',['ORG_ADMIN'])]
        for username,name,roles in configurations:
            user=get_user_model().objects.create_user(username=username,password=password)
            person=Person.objects.create(organization=org,user=user,display_name=name)
            for role in roles:
                RoleGrant.objects.create(organization=org,person=person,role=role)
            if 'AGENT' in roles:
                Membership.objects.create(organization=org,person=person,group=group)
        Asset.objects.create(organization=org,asset_no='PC-001',name='업무용 노트북',model='Business Laptop',location='서울 사무실',portal_visible=True)
        ConfigurationItem.objects.create(organization=org,ci_no='CI-001',name='사내 네트워크',type='NETWORK',portal_visible=True)
        self.stdout.write(self.style.SUCCESS('Created local accounts: employee, agent, manager, orgadmin. Use your chosen password.'))
