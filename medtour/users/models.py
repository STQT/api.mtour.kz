import logging
import random

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from sorl.thumbnail import ImageField

from medtour.users.managers import CustomUserManager, OTPManager
from medtour.utils import SmsApi, unique_slug_generator
from medtour.utils.constants import OrgTypeChoice, UserTypeChoices
from medtour.utils.send_mail import send_email_html


class User(AbstractUser):
    is_organization = models.BooleanField(default=False, verbose_name=_("Организация ли?"))
    email = None
    objects = CustomUserManager()
    REQUIRED_FIELDS = []
    avatar = ImageField(_("Аватар профиля"), upload_to="avatars/%y/%m/%d", null=True, blank=True)
    pick = models.CharField(_("Выбор типа"), max_length=20, choices=UserTypeChoices.choices,
                            default=UserTypeChoices.CLIENT)

    class Meta:
        verbose_name = _("1. Основной аккаунт для аутентификации")
        verbose_name_plural = _("1. Все аккаунты для аутентификации")
        ordering = ("-date_joined",)

    @property
    def is_org(self):
        if hasattr(self, 'organization') and self.organization is not None:
            return True
        return False

    @property
    def related_user(self) -> tuple:
        if hasattr(self, 'people') and self.people is not None:
            return self.people, "people"
        elif hasattr(self, 'organization') and self.organization is not None:
            return self.organization, "organization"
        else:
            return None, None

    @property
    def get_related_user_info(self):
        return self.related_user[0] if self.related_user else None

    def get_related_user_name(self) -> str:
        user_obj = self.get_related_user_info
        if user_obj:
            return ("{} {}".format(user_obj.first_name, user_obj.last_name) if hasattr(self, "people")
                    else user_obj.org_name)
        else:
            return _("Не найдено")

    def send_message_user(self, subject, message,
                          from_email=None, emails: list = None, phone=None, **kwargs):
        """Отправка смс или сообщение в почту"""
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        # SEND TO PHONE
        if phone is None:
            phone_obj = self.phonenumber_set.all()
            if phone_obj.exists():
                phone = str(phone_obj.first())
            else:
                phone = None
        if phone:
            SmsApi.send_sms(
                phones=phone,
                message=message,
            )
        # SEND TO EMAIL
        if emails is None:
            email_qs = self.emailaddress_set.all()
            if email_qs.exists():
                emails = [str(obj) for obj in email_qs]
            else:
                emails = None
        if emails:
            try:
                send_email_html(emails, subject, 'email/index.html',
                                {'title': subject,
                                 'body': message}, from_email=from_email,
                                **kwargs)
            except Exception as e:
                logging.error("Exception sending message to %s: %s", self.email, e)
                return ValidationError({"detail": "Почта не существует {}: {}".format(self.email, e)})

    @cached_property
    def phone_obj(self):
        return self.phonenumber_set.first()

    @cached_property
    def email_obj(self):
        return self.emailaddress_set.first()

    def get_phone(self):
        return self.phone_obj.phone.raw_input if self.phone_obj else None

    def get_email(self):
        return self.email_obj.email if self.email_obj else None


class Person(models.Model):
    user = models.OneToOneField(User,
                                related_name="people",
                                verbose_name=_("Основной аккаунт"),
                                on_delete=models.PROTECT)
    iin = models.CharField(_("ИИН пользователя"), max_length=14, db_index=True, null=True, blank=True)
    first_name = models.CharField(_('Имя'), max_length=150)
    last_name = models.CharField(_('Фамилия'), max_length=150)
    country = models.ForeignKey("users.Country", verbose_name=_("Страна"), related_name="person_countries",
                                on_delete=models.SET_NULL, blank=True, null=True)
    region = models.ForeignKey("users.Region", verbose_name=_("Регион"), related_name="person_regions",
                               on_delete=models.SET_NULL, blank=True, null=True)
    district = models.CharField(_("Район"), max_length=50, null=True, blank=True)
    street = models.CharField(_("Улица"), max_length=50, null=True, blank=True)
    home_number = models.CharField(_("Номер дома"), max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = _("2. Пользователь")
        verbose_name_plural = _("2. Пользователи")
        ordering = ("first_name", "last_name")

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class Organization(models.Model):
    user = models.OneToOneField(User,
                                related_name="organization",
                                verbose_name=_("Основной аккаунт"),
                                on_delete=models.PROTECT)
    org_name = models.CharField(_("Название организации"), max_length=150, null=True, blank=True)
    bin = models.CharField(_("БИН организации"), max_length=12, db_index=True, null=True, blank=True)
    is_moderated = models.BooleanField(_("Проверен"), default=False)
    type = models.CharField(_("Тип организации"), max_length=15, choices=OrgTypeChoice.choices,
                            default=OrgTypeChoice.SANATORIUM)

    def __str__(self):
        return "Организация {}".format(self.org_name if self.org_name else "Без названия")

    class Meta:
        verbose_name = _("3. Организация")
        verbose_name_plural = _("3. Организации")
        ordering = ("is_moderated",)


class OrganizationCategory(models.Model):
    title = models.CharField(_("Title"), max_length=100)
    slug = models.SlugField(_("Слаг"), blank=True, max_length=255)
    photo = models.ImageField(default='/static/images/default.svg', upload_to="banners")
    icon = models.ImageField(default='/static/images/cart.svg', upload_to="category_icons")
    icon_active = models.ImageField(default='/static/images/cart.svg', upload_to="category_icons")
    column = models.CharField(default="two", max_length=10)
    title_color = models.CharField(default="#FFFFFF", max_length=10)

    class Meta:
        verbose_name = _("3.1 Категория организации")
        verbose_name_plural = _("3.1 Категории организаций")
        ordering = ("title",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.title)
        super().save(*args, **kwargs)


class Code(models.Model):
    """
    Example use:
    class OTPCode(Code):
        ...


    obj = OTPCode.objects.create(user=request.user)
    send_mail(subject="OTP code", message=_("OTP password: {code}").format(code=obj.number),
              from_email="example@mail.com", recipient_list=["to@mail.com"])

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OTPManager()

    class Meta:
        ordering = ('-created_at',)
        abstract = True

    def __str__(self):
        return f"{self.number} | {self.created_at}"


class ActivateCode(Code):
    class Meta:
        verbose_name = _("Код подтверждения для активации")
        verbose_name_plural = _("Коды подтверждения для активации")


class RestoreCode(Code):
    class Meta:
        verbose_name = _("Код подтверждения для восстановления")
        verbose_name_plural = _("Коды подтверждения для восстановления")


class Country(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Страна")
        verbose_name_plural = _("Государства")


class Region(models.Model):
    country = models.ForeignKey("users.Country", on_delete=models.CASCADE, related_name="regions")
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _("Область")
        verbose_name_plural = _("Области")


class City(models.Model):
    region = models.ForeignKey("users.Region", on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(_("Слаг"), blank=True, max_length=255)
    is_first_page = models.BooleanField(_("Будет ли на первой странице?"), default=False)

    class Meta:
        ordering = ['name']
        verbose_name = _("Город")
        verbose_name_plural = _("Города")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_name = self.name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug: # noqa
            self.slug = unique_slug_generator(self, self.name)
        if self.name != self.__original_name:
            self.slug = unique_slug_generator(self, self.name)
        super().save(*args, **kwargs)
        self.__original_name = self.name
