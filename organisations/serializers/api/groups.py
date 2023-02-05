from django.contrib.auth import get_user_model
from rest_framework import serializers

from common.serializers.mixins import ExtendedModelSerializer, \
    InfoModelSerializer
from organisations.models.groups import Group
from users.serializers.nested.users import UserShortSerializer


User = get_user_model()


class GroupListSerializer(InfoModelSerializer):
    director = UserShortSerializer()
    pax = serializers.IntegerField()
    groups_count = serializers.IntegerField()
    can_manage = serializers.BooleanField()

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'director',
            'pax',
            'groups_count',
            'created_at',
            'can_manage',
        )


class GroupRetrieveSerializer(InfoModelSerializer):
    director = UserShortSerializer()
    pax = serializers.IntegerField()
    groups_count = serializers.IntegerField()
    can_manage = serializers.BooleanField()

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'director',
            'pax',
            'groups_count',
            'created_at',
            'can_manage',
        )


class GroupCreateSerializer(ExtendedModelSerializer):
    class Meta:
        model = Group
        fields = (
            'id',
            'name',
        )


class GroupUpdateSerializer(ExtendedModelSerializer):
    class Meta:
        model = Group
        fields = (
            'id',
            'name',
        )
