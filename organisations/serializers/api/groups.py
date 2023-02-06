from crum import get_current_user
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from common.serializers.mixins import ExtendedModelSerializer, \
    InfoModelSerializer
from organisations.models.groups import Group
from organisations.models.organisations import Organisation
from organisations.serializers.nested.organisations import \
    OrganisationShortSerializer

User = get_user_model()


class GroupListSerializer(InfoModelSerializer):
    organisation = OrganisationShortSerializer()
    pax = serializers.IntegerField()
    can_manage = serializers.BooleanField()
    is_member = serializers.BooleanField()

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'organisation',
            'pax',
            'created_at',
            'can_manage',
            'is_member',
        )


class GroupRetrieveSerializer(InfoModelSerializer):
    organisation = OrganisationShortSerializer()
    pax = serializers.IntegerField()
    can_manage = serializers.BooleanField()
    is_member = serializers.BooleanField()

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'organisation',
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
        )
        extra_kwargs = {
            'manager': {'required': False, 'allow_null': True, },
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

        # Specified manager or organisation director
        attrs['manager'] = attrs.get('manager') or org.director_employee
        manager = attrs['manager']
        # Check manager
        if manager not in org.employees_info.all():
            raise ParseError(
                'Администратором может быть только сотрудник организации или руководитель.'
            )

        # Check name duplicate
        if self.Meta.model.objects.filter(
                organisation=org, name=attrs['name']
        ).exists():
            raise ParseError(
                'Группа с таким названием уже существует.'
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

    def validate(self, attrs):
        # Check name duplicate
        if self.instance.organisation.groups.filter(name=attrs['name']).exists():
            raise ParseError(
                'Группа с таким названием уже существует.'
            )
        return attrs
