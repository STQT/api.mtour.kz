from rest_framework import permissions


class IsOrganization(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_organization


class IsPeople(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_organization
