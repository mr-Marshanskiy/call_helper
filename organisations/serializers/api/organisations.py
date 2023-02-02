from django.contrib.auth import get_user_model

from common.serializers.mixins import ExtendedModelSerializer
from organisations.models.organisations import Organisation
from users.serializers.nested.users import UserShortSerializer


User = get_user_model()


class OrganisationSearchListSerializer(ExtendedModelSerializer):
    director = UserShortSerializer()

    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
            'director',
        )


class OrganisationListSerializer(ExtendedModelSerializer):
    director = UserShortSerializer()

    class Meta:
        model = Organisation
        fields = '__all__'


class OrganisationRetrieveSerializer(ExtendedModelSerializer):
    director = UserShortSerializer()

    class Meta:
        model = Organisation
        fields = '__all__'


class OrganisationCreateSerializer(ExtendedModelSerializer):
    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
        )


class OrganisationUpdateSerializer(ExtendedModelSerializer):
    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
        )
