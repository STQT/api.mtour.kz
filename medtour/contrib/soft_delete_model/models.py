from django.db.models import Manager, Model, BooleanField, DateTimeField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SoftDeleteManager(Manager):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_deleted=False)


class SoftDeleteModel(Model):
    is_deleted = BooleanField(_("Удалён?"), default=False, help_text=_("Отметьте, если удалён тур"))
    deleted_at = DateTimeField(null=True, blank=True, editable=False)
    objects = Manager()
    undeleted_objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()
