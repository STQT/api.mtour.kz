from rest_framework import permissions

from medtour.tours.models import Tour


class IsTourOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        tour_owner = Tour.objects.select_related("org__user").only("id", 'org__user__id').get(id=obj.id).org.user
        return tour_owner == request.user or request.user.is_superuser
