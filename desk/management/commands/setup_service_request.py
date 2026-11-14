import json,os
from pathlib import Path
from django.core.management.base import BaseCommand,CommandError
from desk.service_request_setup import configure,verify_configuration,USERNAMES
from django.db import transaction
from desk.services import BusinessError

class Command(BaseCommand):
    help='Create the requested service-request workflow, groups and five accounts without resetting existing data.'
    def add_arguments(self,parser):
        parser.add_argument('--organization-id',required=True);parser.add_argument('--password-file')
    def handle(self,*args,**options):
        try:
            passwords=json.loads(Path(options['password_file']).read_text(encoding='utf-8')) if options.get('password_file') else json.loads(os.environ.get('STUDIO_SR_PASSWORDS_JSON','{}'))
            with transaction.atomic():
                result=configure(options['organization_id'],passwords)
                if not result['retained']:result.update(verify_configuration(options['organization_id'],passwords))
        except (BusinessError,ValueError,KeyError) as exc:raise CommandError(exc.message if isinstance(exc,BusinessError) else 'Invalid service-request setup configuration; no credentials printed.') from None
        self.stdout.write('SR_SETUP '+json.dumps(result,ensure_ascii=False))
