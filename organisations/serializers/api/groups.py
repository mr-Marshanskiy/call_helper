from crum import get_current_user
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from common.serializers.mixins import ExtendedModelSerializer, \
    InfoModelSerializer
from organisations.models.groups import Group
from organisations.models.organisations import Organisation

User = get_user_model()


class GroupListSerializer(InfoModelSerializer):
    pax = serializers.IntegerField()
    can_manage = serializers.BooleanField()
    is_member = serializers.BooleanField()

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'pax',
            'created_at',
            'can_manage',
            'is_member',
        )


class GroupRetrieveSerializer(InfoModelSerializer):
    pax = serializers.IntegerField()
    can_manage = serializers.BooleanField()
    is_member = serializers.BooleanField()

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'pax',
            'created_at',
            'can_manage',
            'is_member',
        )


class GroupCreateSerializer(ExtendedModelSerializer):
    class Meta:
        model = Group
        fields = (
            'id',
            'organisation',
            'manager',
            'name',
            'members_info',
        )
        extra_kwargs = {
            'members_info': {'required': False, },
        }

    def validate_organisation(self, value):
        user = get_current_user()
        if value not in Organisation.objects.filter(director=user,):
            return ParseError(
                'Неверно выбрана организация.'
            )
        return value

    def validate(self, attrs):
        org = attrs['organisation']
        manager = attrs.get('manager') or org.director_employee
        if manager not in org.employees.all():
            raise ParseError(
                'Администратором может быть только сотрудник организации или руководитель.'
            )
        return attrs


class GroupUpdateSerializer(ExtendedModelSerializer):

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'members',
        )
