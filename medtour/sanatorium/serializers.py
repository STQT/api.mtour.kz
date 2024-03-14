from django.utils.translation import gettext_lazy as _
from drf_spectacular import types
from drf_spectacular.utils import extend_schema_field
from psycopg2.extras import DateRange
from rest_framework import serializers, exceptions

from medtour.orders.serializers import ServiceCartCountSerializer, WriteServiceCartPackagesSerializer
from medtour.sanatorium.models import Reservations, ReservationsServices, ReservationsPackage
from medtour.tournumbers.models import TourNumbers
from medtour.tourpackages.models import TourPackages
from medtour.tourpackages.serializers import ListPackageSerializer
from medtour.users.serializers import UserReadSerializer


class ReservationsServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationsServices
        fields = ("service", "count")


class ReservationsServicesReadSerializer(serializers.ModelSerializer):
    service_name = serializers.StringRelatedField(source="service.name", read_only=True)

    class Meta:
        model = ReservationsServices
        fields = ("service", "count", "service_name")


class ReservationsSerializer(serializers.ModelSerializer):
    reservator = UserReadSerializer(many=False, required=False, read_only=True)  #
    services = ReservationsServicesSerializer(many=True, required=False, write_only=True)
    package = serializers.PrimaryKeyRelatedField(queryset=TourPackages.objects.all(), required=False,
                                                 write_only=True)
    reservations_services = ReservationsServicesReadSerializer(read_only=True, many=True)  #
    reservations_packages = ListPackageSerializer(read_only=True, many=False,
                                                  source="get_reservation_package")  #
    reservations_start = serializers.DateField(source="reservation_date.lower", read_only=True)
    reservations_end = serializers.DateField(source="reservation_date.upper", read_only=True)
    start = serializers.DateField(write_only=True, required=True)
    end = serializers.DateField(write_only=True, required=True)
    number = serializers.PrimaryKeyRelatedField(queryset=TourNumbers.objects.all(), required=True)
    cart_packages = WriteServiceCartPackagesSerializer(many=True, required=False, read_only=True,
                                                       source="get_cart_packages")  #
    cart_services = ServiceCartCountSerializer(many=True, required=False, read_only=True, source="get_cart_services")  #
    payment_amount = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = Reservations
        exclude = ("reservation_date",)
        extra_kwargs = {
            "approved_status": {"read_only": True},
        }

    @extend_schema_field(types.OpenApiTypes.INT)
    def get_payment_amount(self, instance):
        if hasattr(instance, 'payment'):
            return instance.payment.amount
        return None

    def create(self, validated_data):
        services = validated_data.pop('services', tuple())
        package = validated_data.pop('package', tuple())
        start = validated_data.pop("start")
        end = validated_data.pop("end")
        number_cabinets = validated_data.get("number_cabinets")
        validated_data.update(
            {
                "reservation_date": DateRange(start, end, '[)')
            }
        )
        if number_cabinets is None:
            number = validated_data.get("number")
            empty_cabinets = Reservations.get_empty_cabinets(start, end, number)
            if empty_cabinets.exists():
                validated_data["number_cabinets"] = empty_cabinets.first()
            else:
                raise exceptions.NotAcceptable(
                    detail=_("Все кабинеты заняты в период {} — {} и в номер {}").format(
                        start, end, number
                    ))
        else:
            check_exists = Reservations.check_number_cabinets_is_available(start, end, number_cabinets.id)
            if check_exists:
                raise exceptions.NotAcceptable(
                    detail=_("Этот кабинет занят в период {} — {}").format(
                        start, end
                    ))

        reservation = Reservations.objects.create(**validated_data)
        # SERVICES

        for service_data in services:
            ReservationsServices.objects.create(reservation=reservation, **service_data)

        if package:
            ReservationsPackage.objects.create(reservation=reservation, package=package)
        return reservation


class ReservationsCheckSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    start = serializers.DateField(write_only=True)
    end = serializers.DateField(write_only=True)
    number = serializers.PrimaryKeyRelatedField(queryset=TourNumbers.objects.all(), write_only=True)
