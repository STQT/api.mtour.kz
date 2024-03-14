from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "medtour.users"
    verbose_name = _("2. Аккаунты")

    # def ready(self):
    #     try:
    #         import medtour.users.signals  # noqa F401
    #     except ImportError:
    #         pass
