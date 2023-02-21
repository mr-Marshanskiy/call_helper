from rest_framework.permissions import IsAuthenticated


class IsReplacementManager(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.group.organisation.director == request.user:
            return True
        if obj.group.manager.user == request.user:
            return True
        return False
