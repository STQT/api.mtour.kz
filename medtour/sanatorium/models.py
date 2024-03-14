import calendar
import pprint
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import DateRangeField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from medtour.contrib.soft_delete_model import SoftDeleteModel
from medtour.tournumbers.models import TourNumbers, NumberCabinets
from medtour.tours.models import Tour
from medtour.utils.constants import ReservationApproveStatusChoices

User = get_user_model()


class Reservations(SoftDeleteModel):
    number_cabinets = models.ForeignKey(NumberCabinets, blank=True,
                                        verbose_name=_("Номер комнаты"), on_delete=models.PROTECT,
                                        help_text=_("Выберите комнату для резерва"))
    number = models.ForeignKey(TourNumbers, related_name="reservations", on_delete=models.CASCADE,
                               help_text=_("Указывается кабинет номера"))
    closed_for_repair = models.BooleanField(_("Закрыт на ремонт"), default=False,
                                            help_text=_("Отметить истина, если закрыт на ремонт"))

    reservation_date = DateRangeField()

    paid = models.BooleanField(_("Оплачено"), default=False,
                               help_text=_("Оплачен ли резерв"))
    rated = models.BooleanField(_("Оценено"), default=False,
                                help_text="Оценена ли резервация")
    reservator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                   verbose_name=_("Резервирующий аккаунт"),
                                   help_text=_("Резервирующим может быть и юрлицо и физлицо."))
    amount = models.IntegerField(verbose_name=_("Общая сумма брони"))

    amountOfAdults = models.IntegerField(default=0, blank=True, null=True)
    amountOfChildren = models.IntegerField(default=0, blank=True, null=True)
    fullName = models.CharField(max_length=100, blank=True, null=True)
    phoneNumber = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    partner = models.ForeignKey("users.Organization", on_delete=models.SET_NULL,
                                related_name="partner_reservations",
                                null=True, blank=True)
    tour = models.ForeignKey("tours.Tour", on_delete=models.CASCADE, related_name="san_reservations")
    remarks = models.CharField(_("Примечание"), max_length=50, default='Примечание', null=True, blank=True)
    # TODO: find this revisions
    payment = models.ForeignKey("orders.Payment", on_delete=models.CASCADE, null=True, blank=True,
                                related_name="san_reservations")
    approved_status = models.SmallIntegerField(_("Статус подтверждения"),
                                               choices=ReservationApproveStatusChoices.choices,
                                               default=ReservationApproveStatusChoices.NOT_SENT)

    class Meta:
        verbose_name = _("Бронирование отдельного кабинета тура")
        verbose_name_plural = _("1. Бронь кабинета туров")
        default_related_name = "reservations"

    def __str__(self):
        return "{} | {} | Цена: {}".format(self.tour.title, self.reservation_date, self.amount)

    @classmethod
    def get_free_cabinets(cls):
        # Get the current date and the start and end dates of the current day
        today = date.today()
        year = today.year
        month = today.month
        last_day = calendar.monthrange(year, month)[1]
        last_day_of_month = date(year, month, last_day)
        x = Reservations.objects.filter(reservation_date__overlap=(
            today, last_day_of_month)
        ).values('id', 'reservation_date', 'number_cabinets', 'number').distinct()
        new_data = []
        for booking in x:
            for obj in new_data:
                if obj['number'] == booking['number'] and obj['cabinet'] == booking['number_cabinets']:
                    obj['daterange'].append(booking['reservation_date'])
            new_data.append({
                'number': booking['number'],
                'cabinet': booking['number_cabinets'],
                'daterange': [booking['reservation_date']]
            })
        pprint.pprint(new_data)
        return x

    @classmethod
    def get_all_number_cabinets_with_overlap(cls, start, end):
        # TODO: move this methods to NumberCabinets model methods
        return NumberCabinets.objects.filter(
            Q(reservations__reservation_date__overlap=(start, end)), Q(reservations__is_deleted=False)
        ).prefetch_related("reservations").distinct()

    @classmethod
    def get_all_tour_numbers_id_with_start(cls, start, end, number_id: int):
        return cls.get_all_number_cabinets_with_overlap(start, end).filter(
            reservations__number_id=number_id
        )

    @classmethod
    def get_empty_cabinets(cls, start_date, end, number_id):
        # TODO: Optimize query with prefetch related
        reservations_qs = cls.get_all_tour_numbers_id_with_start(start_date, end, number_id)
        return NumberCabinets.objects.filter(tour_number_id=number_id).exclude(Q(id__in=reservations_qs))

    @classmethod
    def check_number_cabinets_is_available(cls, start_date, end_date, number_cabinets_id):
        return cls.get_all_number_cabinets_with_overlap(start_date, end_date).filter(pk=number_cabinets_id).exists()

    @property
    def get_cart_services(self):
        if hasattr(self, 'payment'):
            if hasattr(self.payment, "cart"):
                return self.payment.cart.get_all_services
        return None

    @property
    def get_cart_packages(self):
        if hasattr(self, "payment"):
            if hasattr(self.payment, "cart"):
                return self.payment.cart.get_all_packages
        return None

    @property
    def get_reservation_package(self):
        if hasattr(self, "reservations_packages"):
            return self.reservations_packages.package
        return None


class ReservationsServices(models.Model):
    reservation = models.ForeignKey(Reservations, related_name='reservations_services',
                                    verbose_name=_("Бронь"), on_delete=models.CASCADE)
    count = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], default=1)
    service = models.ForeignKey("tours.TourPaidServices", null=True, blank=True,
                                related_name="reservations_services",
                                on_delete=models.SET_NULL)


class ReservationsPackage(models.Model):
    reservation = models.OneToOneField(Reservations, related_name='reservations_packages',
                                       verbose_name=_("Бронь"), on_delete=models.CASCADE)
    package = models.ForeignKey("tourpackages.TourPackages",
                                related_name="reservations_packages",
                                on_delete=models.CASCADE)
