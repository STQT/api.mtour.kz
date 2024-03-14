import pytz
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from celery import shared_task

from medtour.sanatorium.models import Reservations
from medtour.utils.constants import PaymentStatusChoices


@shared_task
def reservations_cleaner():
    tz = pytz.timezone(settings.TIME_ZONE)
    ten_minutes_ago = timezone.now().astimezone(tz) - timedelta(minutes=10)
    qs = Reservations.objects.filter(
        payment__created_at__lt=ten_minutes_ago,
        payment__status=PaymentStatusChoices.NOT_PAID,
        is_deleted=False
    ).select_related('payment')
    for reserv_obj in qs:
        if reserv_obj.payment.status == 0:
            reserv_obj.is_deleted = True
            reserv_obj.save()
        else:
            reserv_obj.paid = True
            reserv_obj.save()
