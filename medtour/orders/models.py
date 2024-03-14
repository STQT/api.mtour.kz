from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from medtour.orders.instances import get_pdf_path
from medtour.tournumbers.models import TourNumbers
from medtour.tourpackages.models import TourPackages
from medtour.tours.models import Tour, TourPaidServices
from medtour.utils.constants import CitizenDocType, PersonGender, PaymentStatusChoices

User = get_user_model()


class ServiceCart(models.Model):
    """Корзина тура для проведения оплаты"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="cart",
                             help_text=_("Выбранный тур пользователя"))
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name="cart", null=True, blank=True,
                             help_text=_("Пользователь (нужно указать ID пользователя при регистрации"))
    number = models.ForeignKey(TourNumbers, on_delete=models.CASCADE,
                               verbose_name=_("Номер тура"))
    start = models.DateField(_("Дата начала тура"),
                             help_text=_("Дата начала тура"))
    end = models.DateField(_("Дата окончания тура"),
                           help_text=_("Дата окончания тура"))
    count = models.IntegerField(_("Количество человек"), default=1,
                                help_text=_("Количество человек"))
    price = models.IntegerField(_("Цена"), default=0,
                                help_text=_("Общая цена при покупке тура"))

    def __str__(self):
        return "Тур: {} | Пакет: {} | Дата: {} | Цена: {}".format(self.tour.title if self.tour else None,
                                                                  self.number.title if self.number else None,
                                                                  self.start,
                                                                  self.price)

    class Meta:
        verbose_name = _("Корзина тура")
        verbose_name_plural = _("Корзина туров")

    @property
    def get_all_services(self):
        return self.service_count_services.all()

    @property
    def get_all_packages(self):
        return self.service_count_packages.all()


class ServiceCartServices(models.Model):
    service = models.ForeignKey(TourPaidServices, related_name="service_count_services",
                                verbose_name=_("Платная услуга корзины"), on_delete=models.CASCADE)
    count = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    service_cart = models.ForeignKey(ServiceCart, on_delete=models.CASCADE,
                                     verbose_name=_("Корзина тура"),
                                     related_name="service_count_services")

    class Meta:
        verbose_name = _("Услуга корзины тура")
        verbose_name_plural = _("Услуги корзины тура")


class ServiceCartPackages(models.Model):
    package = models.ForeignKey(TourPackages, related_name="service_count_packages",
                                verbose_name=_("Платная услуга корзины"), on_delete=models.CASCADE)
    count = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    service_cart = models.ForeignKey(ServiceCart, on_delete=models.CASCADE,
                                     verbose_name=_("Корзина тура"),
                                     related_name="service_count_packages")

    class Meta:
        verbose_name = _("Пакет корзины тура")
        verbose_name_plural = _("Пакеты корзины тура")


class ServiceCartVisitors(models.Model):
    service_cart = models.ForeignKey("orders.ServiceCart", on_delete=models.PROTECT,
                                     verbose_name=_("Корзина"), related_name="visitors")
    first_name = models.CharField(_("Имя"), max_length=50)
    last_name = models.CharField(_("Фамилия"), max_length=50)
    birthday_date = models.DateField(_("Дата рождения"))
    citizenship = models.CharField(_("Код страны"), max_length=50)
    document = models.IntegerField(_("Тип документа"), choices=CitizenDocType.choices)
    doc_number = models.CharField(_("Номер документа"), max_length=20)
    gender = models.IntegerField(_("Пол"), choices=PersonGender.choices,
                                 validators=[MinValueValidator(0), MaxValueValidator(1)])

    class Meta:
        verbose_name = _("Посетитель тура")
        verbose_name_plural = _("Посетители тура")

    def __str__(self):
        return str(self.service_cart)


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    amount = models.IntegerField(_("Сумма оплаты"))
    status = models.IntegerField(_("Статус оплаты"), choices=PaymentStatusChoices.choices,
                                 default=PaymentStatusChoices.NOT_PAID)
    created_at = models.DateTimeField(auto_now_add=True)
    cart = models.OneToOneField(ServiceCart, on_delete=models.CASCADE, related_name="payments")
    # TODO: find this revisions
    # reservation = models.OneToOneField("sanatorium.Reservations", on_delete=models.CASCADE,
    #                                    help_text=_("Укажите бронь"), related_name="payment")
    is_partial = models.BooleanField(_("Частичная оплата"), default=False)
    amount_paid_part = models.IntegerField(_("Процент частичной оплаты"), default=100,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)])
    redirect_url = models.CharField(_("Страница с оплатой платежной системы"), max_length=150, null=True, blank=True)
    pdf_file = models.FileField(upload_to=get_pdf_path, blank=True, null=True)

    def __str__(self):
        return "Пользователь: {} | Сумма: {} | Статус: {}".format(self.user, self.amount, self.status)

    class Meta:
        verbose_name = _("Оплата")
        verbose_name_plural = _("Оплаты")


class Transactions(models.Model):
    """Транзакции"""
    check_id = models.CharField(_("check_id"), max_length=25)
    email = models.CharField(_("email"), max_length=100, blank=True, null=True)
    phone = models.CharField(_("phone"), max_length=20, blank=True, null=True)
    total = models.CharField(_("total"), max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)


class GuideOrders(models.Model):
    """Заказы"""
    # TODO: remove CASCADE
    program = models.ForeignKey("guides.Program", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    tour = models.ForeignKey("tours.Tour", on_delete=models.CASCADE)
    transaction = models.ForeignKey("orders.Transactions", on_delete=models.CASCADE)
    count = models.IntegerField(_("Количество"))
    price = models.IntegerField(_("Цена"))
    sum_total = models.IntegerField(_("Итоговая сумма"))
    total = models.IntegerField(_("Общая сумма с применением скидки"), default=sum_total)

    created_at = models.DateTimeField(auto_now_add=True)
