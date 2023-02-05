import django_filters

from organisations.models.groups import Group
from organisations.models.organisations import Organisation, Employee


class OrganisationFilter(django_filters.FilterSet):
    can_manage = django_filters.BooleanFilter('can_manage', label='Can manage')

    class Meta:
        model = Organisation
        fields = ('can_manage', 'id',)


class EmployeeFilter(django_filters.FilterSet):
    is_corporate_account = django_filters.BooleanFilter(
        'user__is_corporate_account', label='Is corporate account'
    )

    class Meta:
        model = Employee
        fields = ('is_corporate_account',)


class GroupFilter(django_filters.FilterSet):

    class Meta:
        model = Group
        fields = ('organisation', 'manager',)
