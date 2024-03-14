from django.db.models.signals import post_save
from django.dispatch import receiver

from medtour.tournumbers.models import TourNumbers, NumberCabinets
from medtour.tournumbers.tasks import create_cabinets


@receiver(post_save, sender=TourNumbers)
def creating_package_cabinets(sender, instance, created, **kwargs):
    if created:
        cabinets_count = instance.place_count
        create_cabinets.delay(instance.id, cabinets_count)
