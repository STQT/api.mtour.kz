from django.db.models import Q
from rest_framework import viewsets, generics
from rest_framework.exceptions import PermissionDenied

from medtour.applications.serializers import (ListTourApplicationSerializer,
                                              PostApplicationSerializer, UpdateTourApplicationSerializer,
                                              RetrieveTourApplicationSerializer, CommentTourApplicationSerializer)
from medtour.applications.models import TourApplication, Application, CommentTourApplication
from medtour.contrib.pagination import StandardResultsSetPagination
from medtour.contrib.serializers import ReadWriteSerializerMixin


class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = PostApplicationSerializer


class TourApplicationViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    queryset = TourApplication.objects.all().order_by('tour')
    serializer_class = ListTourApplicationSerializer
    read_serializer_class = ListTourApplicationSerializer
    write_serializer_class = UpdateTourApplicationSerializer
    retrieve_serializer_class = RetrieveTourApplicationSerializer
    http_method_names = ["get", "put", "patch"]
    filterset_fields = ["tour_id"]
    list_select_related = ("tour__org",)
    list_prelated_tuple = ("application_comments",)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if not hasattr(self.request.user, 'organization'):  # noqa
            raise PermissionDenied
        qs = self.queryset
        query = Q(tour__org=self.request.user.organization)

        # for list views
        if self.action == "list":
            query.add(Q(tour_id=self.request.query_params.get('tour_id')), Q.OR)
            return qs.filter(query).select_related(*self.list_select_related)

        # for self.get_object()
        return qs.filter(query).select_related("tour__org").prefetch_related(*self.list_prelated_tuple)
        # return super().get_queryset()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return self.get_write_serializer_class()
        elif self.action == "retrieve":
            return self.retrieve_serializer_class
        return self.get_read_serializer_class()


class CommentTourApplicationViewSet(viewsets.ModelViewSet):
    queryset = CommentTourApplication.objects.all()
    serializer_class = CommentTourApplicationSerializer
    http_method_names = ["post", "put", "patch", "delete"]
