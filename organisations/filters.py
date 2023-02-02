import pdb

import django_filters

from organisations.models.organisations import Organisation


class OrganisationFilter(django_filters.FilterSet):
    can_manage = django_filters.BooleanFilter('can_manage', label='Can manage')

    class Meta:
        model = Organisation
        fields = ('can_manage', 'id',)
