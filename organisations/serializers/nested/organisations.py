from common.serializers.mixins import ExtendedModelSerializer
from organisations.models.organisations import Organisation


class OrganisationShortSerializer(ExtendedModelSerializer):
    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
        )
