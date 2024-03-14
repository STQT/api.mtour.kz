from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from medtour.contrib.required_field_list_view.mixins import TourIdListModelMixin, TourNumberIdListModelMixin
from medtour.contrib.soft_delete_model.mixins import SoftDestroyModelMixin


class TourIdRequiredFieldsModelViewSet(mixins.CreateModelMixin,
                                       mixins.RetrieveModelMixin,
                                       mixins.UpdateModelMixin,
                                       mixins.DestroyModelMixin,
                                       TourIdListModelMixin,
                                       GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions with *`tour_id`* parameter.
    """
    pass


class TourNumberRequiredFieldsModelViewSet(mixins.CreateModelMixin,
                                           mixins.RetrieveModelMixin,
                                           mixins.UpdateModelMixin,
                                           mixins.DestroyModelMixin,
                                           TourNumberIdListModelMixin,
                                           GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass


class TourIdRequiredSoftDeleteModelViewSet(mixins.CreateModelMixin,
                                           mixins.RetrieveModelMixin,
                                           mixins.UpdateModelMixin,
                                           SoftDestroyModelMixin,
                                           TourIdListModelMixin,
                                           GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass


class TourNumberRequiredSoftDeleteModelViewSet(mixins.CreateModelMixin,
                                               mixins.RetrieveModelMixin,
                                               mixins.UpdateModelMixin,
                                               SoftDestroyModelMixin,
                                               TourNumberIdListModelMixin,
                                               GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass
