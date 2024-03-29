from django.db import models
from django.utils.translation import gettext_lazy as _


class PersonGender(models.IntegerChoices):
    MALE = 0, _("Мужчина")
    FEMALE = 1, _("Женщина")


class CitizenDocType(models.IntegerChoices):
    CERTIFICATE = 0, _("Удостоверение личности")
    PASSPORT = 1, _("Паспорт")
    BIRT_CERTIFICATE = 2, _("Свидетельство о рождении")


class CurrencyChoice(models.IntegerChoices):
    USD = 0, "USD"
    KZT = 1, "KZT"
    UZS = 2, "UZS"
    KGS = 3, "KGS"
    EUR = 4, "EUR"


class WeekDayChoice(models.IntegerChoices):
    MONDAY = 1, _("ПОНЕДЕЛЬНИК")
    TUESDAY = 2, _("ВТОРНИК")
    WEDNESDAY = 3, _("СРЕДА")
    THURSDAY = 4, _("ЧЕТВЕРГ")
    FRIDAY = 5, _("ПЯТНИЦА")
    SATURDAY = 6, _("СУББОТА")
    YESTERDAY = 0, _("ВОСКРЕСЕНЬЕ")


class OrgTypeChoice(models.TextChoices):
    SANATORIUM = "sanatorium", _("Санаторий")
    ZONAOTDYXA = "zonaotdyxa", _("Зона отдыха")
    GUIDE = "guide", _("Гиды")


class GuideComplexityChoice(models.TextChoices):
    EASY = "easy", _("Лёгкий")
    MEDIUM = "medium", _("Средний")
    HARD = "hard", _("Сложный")


class GuideDurationTypeChoice(models.TextChoices):
    MINUTES = "minutes", _("Минут")
    HOURS = "hours", _("Час")
    DAYS = "days", _("День")
    WEEKS = "weeks", _("Неделя")


class UserTypeChoices(models.TextChoices):
    RESORT = "resort"
    GUIDE = "guide"
    CLIENT = "client"


class ReservationApproveStatusChoices(models.IntegerChoices):
    NOT_SENT = -1, _("Сообщение не отправлено")
    SENT = 0, _("Сообщение отправлено")
    APPROVED = 1, _("Подтверждено")


class PaymentStatusChoices(models.IntegerChoices):
    NOT_PAID = 0, _("Не оплачено")
    PAID = 1, _("Оплачено")
