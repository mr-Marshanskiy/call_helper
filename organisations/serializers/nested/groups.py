from common.serializers.mixins import ExtendedModelSerializer
from organisations.models.groups import Group
from organisations.serializers.nested.employees import EmployeeShortSerializer
from organisations.serializers.nested.organisations import \
    OrganisationShortSerializer


class GroupShortSerializer(ExtendedModelSerializer):
    organisation = OrganisationShortSerializer()
    manager = EmployeeShortSerializer()

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'organisation',
            'manager',
        )
