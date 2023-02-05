from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsMyOrganisation(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.director == request.user:
            return True

        if request.method not in SAFE_METHODS:
            return obj.employees == request.user

        return False


class IsColleagues(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.organisation.director == request.user:
            return True

        if request.method in SAFE_METHODS:
            return request.user in obj.organisation.employees
        return False


class IsMyGroup(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.director == request.user:
            return True

        if request.method not in SAFE_METHODS:
            return obj.employees == request.user
        return False
