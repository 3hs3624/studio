import json,os
from pathlib import Path
from django.core.management.base import BaseCommand,CommandError
from desk.service_request_demo import configure
from desk.services import BusinessError
class Command(BaseCommand):
    help='Prepare role users, versioned SR template, satisfaction flow and five sample requests; never resets passwords.'
    def add_arguments(self,parser):
        parser.add_argument('--organization-id',required=True);parser.add_argument('--password-file');parser.add_argument('--no-samples',action='store_true')
    def handle(self,*args,**opts):
        try:
            passwords=json.loads(Path(opts['password_file']).read_text(encoding='utf-8')) if opts.get('password_file') else json.loads(os.environ.get('STUDIO_SR_DEMO_PASSWORDS_JSON','{}'))
            result=configure(opts['organization_id'],passwords,not opts['no_samples'])
        except (BusinessError,ValueError,KeyError) as exc:raise CommandError(exc.message if isinstance(exc,BusinessError) else 'Invalid demo configuration; no credentials printed.') from None
        self.stdout.write('SR_DEMO '+json.dumps(result,ensure_ascii=False))
