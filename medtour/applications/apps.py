from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medtour.applications'

    def ready(self):
        import medtour.applications.signals # noqa
