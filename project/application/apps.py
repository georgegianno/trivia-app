from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'project.application'

    def ready(self):
        from . import signals
        super().ready()