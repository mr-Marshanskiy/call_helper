from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsMyOrganisation(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.director == request.user:
            return True

        if request.method in SAFE_METHODS:
            return obj.employees.all(user=request.user).exists()

        return False


class IsColleagues(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.organisation.director == request.user:
            return True

        if request.method in SAFE_METHODS:
            return obj.organisation.employees.all(user=request.user).exists()
        return False


class IsMyGroup(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.organisation.director == request.user:
            return True

        if request.method in SAFE_METHODS:
            return obj.organisation.employees.all(user=request.user).exists()
        return False


class IsOfferManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.organisation.director == request.user:
            return True
        return False
