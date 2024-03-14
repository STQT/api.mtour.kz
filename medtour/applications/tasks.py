from celery import shared_task

from medtour.applications.models import TourApplication
from medtour.tours.models import Tour


@shared_task
def save_application_for_all_tours(application_id: int, name, phone):
    tours = Tour.objects.all()
    TourApplication.objects.bulk_create(
        [
            TourApplication(tour=tour, application_id=application_id)
            for tour in tours
        ]
    )
    # TODO: https://mtour.kz/api/dashboard/applications/application/31/change/

    import requests
    from django.conf import settings
    data = {
        "chat_id": settings.APPLICATION_SEND_BOT_GROUP_ID,
        "text": "Новая заявка: \n"
                f"Имя: {name}\n"
                f"Телефон: {phone}\n"
    }
    url = f"https://api.telegram.org/bot{settings.APPLICATION_SEND_BOT_TOKEN}/sendMessage"
    x = requests.post(url=url,
                      data=data)
    return x.text
