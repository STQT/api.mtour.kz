from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GuidesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medtour.guides'
    verbose_name = _("Гиды")
