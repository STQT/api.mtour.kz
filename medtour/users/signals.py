from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Organization, Person

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # NOTE: Never convert this to an asynchronous task, because it is used in api response
    if created and instance.is_organization:
        Organization.objects.create(user=instance,
                                    bin="",)
    elif created:
        Person.objects.create(user=instance,
                              iin="",)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.related_user[0]:
        return instance.related_user[0].save()
