from django.conf import settings
from django.utils.translation import gettext_lazy as _, gettext_lazy
from psycopg2._range import DateRange  # noqa
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError

from medtour.contrib.exceptions import PaymentError
from medtour.orders.models import ServiceCartServices, Payment, ServiceCart, ServiceCartPackages, ServiceCartVisitors
from medtour.paycredentials.models import Kassa24Credentials
from medtour.sanatorium.models import Reservations
from medtour.tournumbers.models import TourNumbers
from medtour.tourpackages.serializers import ListPackageSerializer
from medtour.tourpackages.models import TourPackages
from medtour.tours.serializers import TourPaidServicesSerializer
from medtour.tours.models import Tour
from medtour.utils.constants import OrgTypeChoice
from medtour.utils.payment import PaymentApi


class ServiceCartVisitorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCartVisitors
        exclude = ('id', 'service_cart')


class ServiceCartCountSerializer(serializers.ModelSerializer):
    service = TourPaidServicesSerializer(many=False, required=True)

    class Meta:
        model = ServiceCartServices
        fields = "__all__"


class WriteServiceCartCountSerializer(serializers.ModelSerializer):
    price = serializers.StringRelatedField(source="service.price", read_only=True)

    class Meta:
        model = ServiceCartServices
        fields = ("service", "count", "price")


class PaymentSerializer(serializers.ModelSerializer):
    # cart = ServiceCartSerializerRead(many=True)

    class Meta:
        fields = "__all__"
        model = Payment


class ServiceCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    services = ServiceCartCountSerializer(many=True, required=False, read_only=True)
    packages = ListPackageSerializer(many=True, required=False, read_only=True)
    payments = PaymentSerializer(read_only=True, many=False)

    class Meta:
        model = ServiceCart
        fields = "__all__"


class WriteServiceCartPackagesSerializer(serializers.ModelSerializer):
    price = serializers.StringRelatedField(source="package.price", read_only=True)

    class Meta:
        model = ServiceCartPackages
        fields = ("package", "count", "price")


class WriteServiceCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    services = WriteServiceCartCountSerializer(many=True, required=False)
    package = WriteServiceCartPackagesSerializer(many=False, required=False)
    number = serializers.PrimaryKeyRelatedField(queryset=TourNumbers.objects.all(), required=False)
    payments = PaymentSerializer(many=False, read_only=True)
    error = serializers.BooleanField(default=False, read_only=True)
    error_msg = serializers.CharField(read_only=True, default=None, allow_null=True)
    visitors = ServiceCartVisitorsSerializer(many=True, required=True)

    class Meta:
        model = ServiceCart
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = None
        self.end_date = None
        self.number_cabinets = None
        self.pay_amount = None
        self.tour = None
        self.tour_type = None
        self.package_data = None
        self.services_data = None
        self.visitors = None
        self.kassa24 = None

    def validate(self, data):
        print("validating")
        self.services_data = data.pop('services', tuple())
        self.package_data = data.pop('package', TourPackages.objects.none())
        self.visitors = data.pop('visitors', ServiceCartVisitors.objects.none())
        self.user = data.pop('user')
        self.tour: Tour = data.get("tour")
        self.tour_type: str = self.tour.org.type

        # Validations
        errors = {}

        if data.get('number') is None and not self.package_data:
            errors["package"] = [_('Вы не выбрали ни одного номера и пакета'), ]
            errors["number"] = [_('Вы не выбрали ни одного номера и пакета'), ]

        if self.package_data:
            data['number'] = self.package_data.get('package').number

        if self.visitors == ServiceCartVisitors.objects.none():
            errors['visitors'] = [_('Вы не указали ни одного посетителя')]

        if errors:
            raise ValidationError(errors)

        kassa24_obj: Kassa24Credentials = self.tour.kassa24 if hasattr(self.tour, 'kassa24') else None
        if kassa24_obj:
            print("validating2")
            kassa24_login = kassa24_obj.login
            kassa24_password = kassa24_obj.password
        else:
            kassa24_login = settings.KASSA24_LOGIN
            kassa24_password = settings.KASSA24_PASSWORD
        self.kassa24 = PaymentApi(kassa24_login, kassa24_password)

        # Check reserved
        self.start_date = data.pop("start")
        self.end_date = data.pop("end")
        self.number = data.get("number")
        self.pay_amount = data.get("price", 0)

        if self.tour_type in [OrgTypeChoice.ZONAOTDYXA]:
            empty_cabinets = Reservations.get_empty_cabinets(self.start_date, self.end_date, self.number)
            if empty_cabinets.exists():
                self.number_cabinets = empty_cabinets.first()
            else:
                raise exceptions.NotAcceptable(
                    detail=_("Все кабинеты заняты в период {} — {} и в номер {}").format(
                        self.start_date, self.end_date, self.number
                    ))
        else:
            print("validating4")
            empty_cabinets = Reservations.get_empty_cabinets(self.start_date, self.end_date, self.number)
            if empty_cabinets.count() > len(self.visitors):
                self.number_cabinets = empty_cabinets
            else:
                raise exceptions.NotAcceptable(
                    detail=_("Все кабинеты заняты в период {} — {} и в номер {}").format(
                        self.start_date, self.end_date, self.number
                    ))
        return data

    def create(self, validated_data):
        # STEP 1: Create service cart from the server
        service_cart = ServiceCart.objects.create(start=self.start_date, end=self.end_date, user=self.user,
                                                  **validated_data)

        # STEP 2: Create service cart check
        # SERVICES
        if self.services_data:
            ServiceCartServices.objects.bulk_create(
                [
                    ServiceCartServices(service_cart=service_cart, **service_data)
                    for service_data in self.services_data
                ]
            )

        # PACKAGE
        if self.package_data:
            ServiceCartPackages.objects.create(service_cart=service_cart, **self.package_data)

        # STEP 3: Create Visitors data
        ServiceCartVisitors.objects.bulk_create(
            [
                ServiceCartVisitors(service_cart=service_cart, **visitors_data)
                for visitors_data in self.visitors
            ]
        )
        # STEP 5: Create payment requisites for user
        resp_text, error = self.kassa24.create_payment(amount=self.pay_amount,  # TODO: calculate amount to self.pay_amount,
                                                       service_cart_id=service_cart.pk,
                                                       email=self.user.get_email(),
                                                       phone=self.user.get_phone()
                                                       )
        # STEP 4: Create reservation from the server
        if error is False:
            payment_obj = Payment.objects.create(user=self.user, cart=service_cart,
                                                 amount=self.pay_amount,  # TODO: calculate amount to self.pay_amount,
                                                 redirect_url=resp_text)
            # TODO: Convert this code to celery task delay
            self.user.send_message_user('Ваша заявка принята',
                                        'Ваша заявка принята, просим оплатить в течении 10 минут')
        else:
            service_cart.error_msg = gettext_lazy("Ошибка платежной системы с содержанием: {}").format(resp_text)
            service_cart.error = True
            raise PaymentError(
                detail=gettext_lazy('Ошибка платежной системы, повторите еще раз. Error Text: {}').format(
                    resp_text
                ))
        if self.tour.org.type in [OrgTypeChoice.ZONAOTDYXA]:
            # One reservation creating
            Reservations.objects.create(
                reservation_date=DateRange(self.start_date, self.end_date, '[)'),
                number=self.number,
                number_cabinets=self.number_cabinets,
                reservator=self.user,
                amountOfAdults=validated_data.get("count", 1),
                tour=self.tour,
                amount=self.pay_amount,
                fullName=self.user.get_related_user_name(),
                phoneNumber=self.user.get_phone(),
                email=self.user.get_email(),
                payment_fk=payment_obj
            )
        else:
            # More reservation creating
            reservation_obj_list = []
            cabinets = self.number_cabinets[:len(self.visitors)]  # QuerySet
            for num, _ in enumerate(self.visitors):
                reservation = Reservations(
                    reservation_date=DateRange(self.start_date, self.end_date, '[)'),
                    number=self.number,
                    number_cabinets=cabinets[num],
                    reservator=self.user,
                    amountOfAdults=validated_data.get("count", 1),
                    tour=self.tour,
                    amount=self.pay_amount,
                    fullName=self.user.get_related_user_name(),
                    phoneNumber=self.user.get_phone(),
                    email=self.user.get_email(),
                    payment_fk=payment_obj
                )
                reservation_obj_list.append(reservation)
            Reservations.objects.bulk_create(reservation_obj_list)
            return service_cart
