from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.serializers.mixins import ExtendedModelSerializer, \
    InfoModelSerializer
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


class OrganisationListSerializer(InfoModelSerializer):
    director = UserShortSerializer()
    pax = serializers.IntegerField()
    groups_count = serializers.IntegerField()
    can_manage = serializers.BooleanField()

    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
            'director',
            'pax',
            'groups_count',
            'created_at',
            'can_manage',
        )


class OrganisationRetrieveSerializer(InfoModelSerializer):
    director = UserShortSerializer()
    pax = serializers.IntegerField()
    groups_count = serializers.IntegerField()
    can_manage = serializers.BooleanField()

    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
            'director',
            'pax',
            'groups_count',
            'created_at',
            'can_manage',
        )


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
