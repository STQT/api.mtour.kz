from celery import shared_task
from django.db import IntegrityError

from medtour.tours.models import TourBookingHoliday, TourBookingWeekDays


@shared_task
def create_days(tour_id):
    try:
        TourBookingWeekDays.objects.create(tour_id=tour_id)
        TourBookingHoliday.objects.create(tour_id=tour_id)
    except IntegrityError:
        pass
