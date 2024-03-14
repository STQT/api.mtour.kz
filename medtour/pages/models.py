from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.utils.translation import gettext_lazy as _


class Common(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextUploadingField()
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{} | {}".format(self.pk, self.created_at.strftime('%d-%m-%Y'))


class PublicOffer(Common):
    class Meta:
        verbose_name = _("Публичная оферта")
        verbose_name_plural = _("Публичная оферта")


class PublicOfferForIndividual(Common):
    class Meta:
        verbose_name = _("Публичная оферта для физических лиц")
        verbose_name_plural = _("Публичная оферта для физических лиц")


class SiteRules(Common):
    class Meta:
        verbose_name = _("Правила пользования сайтом")
        verbose_name_plural = _("Правила пользования сайтом")


class Refunds(Common):
    class Meta:
        verbose_name = _("Правила возврата денежных средств")
        verbose_name_plural = _("Правила возврата денежных средств")


class PersonalInfoProtection(Common):
    class Meta:
        verbose_name = _("Защита персональных данных пользователей")
        verbose_name_plural = _("Защита персональных данных пользователей")


class OrderRules(Common):
    class Meta:
        verbose_name = _("Порядок оформления заказа")
        verbose_name_plural = _("Порядок оформления заказа")
