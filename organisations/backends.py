from rest_framework.filters import BaseFilterBackend


class OwnedByOrganisation(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        org_id = request.parser_context['kwargs'].get('pk')
        return queryset.filter(organisation_id=org_id)
