from django.db import models
from django.utils.translation import gettext_lazy as _

from medtour.tours.models import Tour


class Application(models.Model):
    fullName = models.CharField(_("Полное имя"), max_length=200)
    phoneNumber = models.CharField(_("Телефонный номер"), max_length=16)
    region = models.ForeignKey("users.Region", verbose_name=_("Регион"), on_delete=models.CASCADE)
    category = models.ForeignKey("users.OrganizationCategory",
                                 on_delete=models.CASCADE,
                                 verbose_name=_("Тип тура"),
                                 related_name="applications")
    description = models.TextField(_("Описание"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Заявка тура")
        verbose_name_plural = _("Заявки туров")
        ordering = ["-created_at"]

    def __str__(self):
        return "{} | {}".format(self.fullName, self.category.title)


class TourApplication(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    status = models.BooleanField(_("Статус"), default=False)

    class Meta:
        verbose_name = _("Заявка индивидуального тура")
        verbose_name_plural = _("Заявки индивидуального туров")

    def __str__(self):
        return "{} | Тур: {}".format(self.application.fullName, self.tour.title)


class CommentTourApplication(models.Model):
    tour_application = models.ForeignKey(TourApplication, on_delete=models.CASCADE,
                                         related_name="application_comments")
    comment = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Примечание индивидуальной заявки к туру')
        verbose_name_plural = _('Примечания индивидуальной заявки к турам')

    def __str__(self):
        return "Тур: {} | {}".format(self.tour_application.tour.title, self.tour_application.application.fullName)
