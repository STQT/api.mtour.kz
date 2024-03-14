from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from medtour.subscriptions.models import TourSubscribe, SubscribePrice
from medtour.tours.models import Tour
from medtour.utils.payment import PaymentApi


class CreateSubscribeSerializer(serializers.ModelSerializer):
    payment_link = serializers.CharField(read_only=True, allow_null=True)
    tour = serializers.PrimaryKeyRelatedField(queryset=Tour.objects.all(), write_only=True)
    subscribe_price = serializers.PrimaryKeyRelatedField(queryset=SubscribePrice.objects.all(), write_only=True)
    error = serializers.BooleanField(read_only=True, default=False)
    error_msg = serializers.CharField(read_only=True, default=None, allow_null=True)

    class Meta:
        model = TourSubscribe
        fields = ("tour", "subscribe_price", "payment_link", "error", "error_msg")

    def create(self, validated_data):
        instance = super().create(validated_data)
        payment_obj = PaymentApi(settings.KASSA24_LOGIN, settings.KASSA24_PASSWORD)
        resp_text, error = payment_obj.create_payment(instance.subscribe_price.price)
        if error is False:
            instance.payment_link = resp_text
        else:
            instance.payment_link = None
            instance.error = True
            instance.error_msg = _("Ошибка платежной системы")
        instance.save()
        return instance


class TourSubscribeSerializer(serializers.ModelSerializer):
    overdue = serializers.BooleanField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)

    class Meta:
        model = TourSubscribe
        exclude = "payment_receipt",


class SubscribePricesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribePrice
        exclude = ["is_actual", "created_at"]
