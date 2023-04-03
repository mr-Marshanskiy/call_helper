from crum import get_current_user
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class OwnedByOrganisation(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        org_id = request.parser_context['kwargs'].get('pk')
        user = get_current_user()
        return queryset.filter(
            organisation_id=org_id,
            organisation__employees=user,
        )


class OwnedByGroup(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        group_id = request.parser_context['kwargs'].get('pk')
        user = get_current_user()
        return queryset.filter(
            group_id=group_id,
            group__organisation__employees=user,
        )


class MyOrganisation(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        return queryset.filter(
            Q(director=user) | Q(employees=user)
        ).distinct()


class MyGroup(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        return queryset.filter(
            Q(organisation__director=user) | Q(organisation__employees=user)
        ).distinct()
