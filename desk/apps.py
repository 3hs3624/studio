from django.apps import AppConfig

class DeskConfig(AppConfig):
    name = 'desk'
    def ready(self):
        from . import security  # noqa: F401
