from rest_framework.permissions import BasePermission, SAFE_METHODS, \
    IsAuthenticated


class IsMyOrganisation(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.director == request.user:
            return True

        if request.method in SAFE_METHODS:
            return request.user in obj.employees.all()

        return False


class IsColleagues(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.organisation.director == request.user:
            return True

        if request.method in SAFE_METHODS:
            return request.user in obj.organisation.employees.all()
        return False


class IsMembers(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if (
            obj.group.organisation.director == request.user
            or obj.group.manager.user == request.user
        ):
            return True

        if request.method in SAFE_METHODS:
            return request.user in obj.group.organisation.employees.all()
        return False


class IsMyGroup(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.organisation.director == request.user:
            return True

        if request.method in SAFE_METHODS:
            return request.user in obj.organisation.employees.all()
        return False


class IsOfferManager(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.organisation.director == request.user:
            return True
        return False
