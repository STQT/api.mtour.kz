from celery import shared_task
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from phone_auth.models import EmailAddress, PhoneNumber

from config import celery_app
from medtour.users.models import ActivateCode, Person, Organization

User = get_user_model()


@celery_app.task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@shared_task
def after_create_user_func(user_pk, email=None, phone=None):
    """Отправка кода пользователю"""
    user = User.objects.get(user_id=user_pk)
    if phone:
        PhoneNumber.objects.create(user_=user_pk, phone=phone)
    if email:
        EmailAddress.objects.create(user_id=user_pk, email=email)
    code = ActivateCode.objects.create(user_id=user_pk)

    message = _('Ссылка: {}/activate/?userId={}&code={}').format(
        Site.objects.get_current().domain,
        user_pk,
        str(code.number)
    )
    if email:
        user.send_message_user(subject=settings.DEFAULT_FROM_EMAIL,
                               from_email=settings.DEFAULT_FROM_EMAIL,
                               message=message,
                               emails=[email])
    if phone:
        user.send_message_user(subject=settings.DEFAULT_FROM_EMAIL,
                               message=message,
                               phone=str(phone))


@shared_task
def create_person(user_id: User, first_name, last_name):
    Person.objects.create(user_id=user_id, first_name=first_name, last_name=last_name)


@shared_task
def create_partner(user_id, org_name, org_type):
    Organization.objects.create(user_id=user_id, org_name=org_name, type=org_type)
