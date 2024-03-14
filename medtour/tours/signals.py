from django.db.models.signals import post_save
from django.dispatch import receiver

from medtour.tours.models import Tour, TourBookingWeekDays
from medtour.tours.tasks import create_days

@receiver(post_save, sender=Tour)
def create_weekday(sender, instance, created, **kwargs):
    if created:
        create_days.delay(instance.id)
