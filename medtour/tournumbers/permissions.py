from rest_framework import permissions

from medtour.tournumbers.models import TourNumbers


class IsTourNumberOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.method in permissions.SAFE_METHODS:
            return True
        tournumber_owner = TourNumbers.objects.select_related("tour__org__user").only("id", 'tour__org__user__id').get(
            id=obj.id).tour.org.user
        return tournumber_owner == request.user
