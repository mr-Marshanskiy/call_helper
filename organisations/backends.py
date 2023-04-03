from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class OwnedByOrganisation(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        org_id = request.parser_context['kwargs'].get('pk')
        return queryset.filter(organisation_id=org_id)


class OwnedByGroup(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        group_id = request.parser_context['kwargs'].get('pk')
        return queryset.filter(group_id=group_id)


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
