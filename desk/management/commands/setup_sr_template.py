import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from desk.models import Organization
from desk.services import BusinessError
from desk.sr_template_setup import configure, create_samples


class Command(BaseCommand):
    help = ('IT 서비스 요청(개발·운영) 템플릿: 역할별 사용자, 디자이너 화면 템플릿, 결재선·워크플로우, '
            '카탈로그, 기준정보, 예시 요청 5건을 구성합니다. 기존 계정·구성은 덮어쓰지 않습니다.')

    def add_arguments(self, parser):
        parser.add_argument('--organization-id', help='생략하면 조직이 하나일 때 그 조직을 사용합니다.')
        parser.add_argument('--password-file', help='새로 만들 계정의 초기 비밀번호 JSON {"developer1": "...", ...}')
        parser.add_argument('--skip-samples', action='store_true', help='예시 요청을 만들지 않습니다.')

    def handle(self, *args, **options):
        try:
            org_id = options.get('organization_id') or os.environ.get('STUDIO_SR_TEMPLATE_ORGANIZATION_ID', '')
            if not org_id:
                orgs = list(Organization.objects.values_list('id', flat=True)[:2])
                if len(orgs) != 1:
                    raise CommandError('조직이 하나가 아니므로 --organization-id를 지정하십시오.')
                org_id = str(orgs[0])
            raw = Path(options['password_file']).read_text(encoding='utf-8') if options.get('password_file') else os.environ.get('STUDIO_SR_TEMPLATE_PASSWORDS_JSON', '{}')
            passwords = json.loads(raw or '{}')
            if not isinstance(passwords, dict) or any(not isinstance(v, str) for v in passwords.values()):
                raise ValueError()
            result = configure(org_id, passwords)
            if not options['skip_samples']:
                result['samples'] = create_samples(org_id)
        except BusinessError as exc:
            raise CommandError(exc.message) from None
        except (ValueError, KeyError, Organization.DoesNotExist):
            raise CommandError('서비스요청 템플릿 구성값을 확인하십시오. 비밀번호는 출력하지 않습니다.') from None
        self.stdout.write('SR_TEMPLATE ' + json.dumps(result, ensure_ascii=False))
