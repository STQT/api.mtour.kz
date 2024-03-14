from celery import shared_task

from medtour.tournumbers.models import NumberCabinets


@shared_task
def create_cabinets(pk, cabinets_count):
    for i in range(cabinets_count):
        NumberCabinets.objects.create(tour_number_id=pk, number=i + 1,
                                      humanize_name=i + 1)
