from django.db import models
from django.utils.translation import gettext_lazy as _


class Kassa24Credentials(models.Model):
    tour = models.OneToOneField("tours.Tour", related_name="kassa24", on_delete=models.CASCADE)
    login = models.CharField(max_length=255, verbose_name=_("Логин"))
    password = models.CharField(max_length=255, verbose_name=_("Пароль"))
    is_test = models.BooleanField(_("Это тест?"), default=True)

    class Meta:
        verbose_name = _("Платежные данные касса24")
        verbose_name_plural = _("Платежные данные касса24")

    # def __str__(self):
    #     return str(self.tour)
