from rest_framework import mixins, viewsets

from medtour.contrib.soft_delete_model.mixins import SoftDestroyModelMixin


class SoftDeleteModelViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             SoftDestroyModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
