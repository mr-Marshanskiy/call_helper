from crum import get_current_user
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from common.serializers.mixins import ExtendedModelSerializer
from organisations.constants import OPERATOR_POSITION
from organisations.models.dicts import Position
from organisations.models.organisations import Employee, Organisation
from organisations.serializers.nested.dicts import PositionShortSerializer
from users.serializers.nested.users import UserEmployeeSerializer

User = get_user_model()


class EmployeeSearchSerializer(ExtendedModelSerializer):
    user = UserEmployeeSerializer()
    position = PositionShortSerializer()

    class Meta:
        model = Employee
        fields = (
            'id',
            'position',
            'user',
        )


class EmployeeListSerializer(ExtendedModelSerializer):
    user = UserEmployeeSerializer()
    position = PositionShortSerializer()

    class Meta:
        model = Employee
        fields = (
            'id',
            'date_joined',
            'user',
            'position',
        )


class EmployeeRetrieveSerializer(ExtendedModelSerializer):
    user = UserEmployeeSerializer()
    position = PositionShortSerializer()

    class Meta:
        model = Employee
        fields = (
            'id',
            'date_joined',
            'user',
            'position',
        )


class EmployeeCreateSerializer(ExtendedModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'password',
            'position',
        )

    def validate(self, attrs):
        current_user = get_current_user()

        organisation_id = self.context['view'].kwargs.get('pk')
        organisation = Organisation.objects.filter(
            id=organisation_id, director=current_user,
        ).first()

        # Проверка, что пользователь - владелец организации
        if not organisation:
            raise ParseError(
                'Такой организации не найдено.'
            )

        attrs['organisation'] = organisation

        return attrs

    def create(self, validated_data):
        user_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'is_corporate_account': True,
        }

        with transaction.atomic():
            user = User.objects.create_user(**user_data)
            validated_data['user'] = user

            instance = super().create(validated_data)
        return instance


class EmployeeUpdateSerializer(ExtendedModelSerializer):
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.filter(is_active=True)
    )

    class Meta:
        model = Employee
        fields = (
            'position',
        )

    def validate(self, attrs):
        if self.instance.is_director:
            raise ParseError(
                'Руководитель организации недоступен для изменений.'
            )
        return attrs

    def validate_position(self, value):
        if value.code == OPERATOR_POSITION:
            if self.instance.is_manager:
                employee_groups = self.instance.groups_managers.values_list('name', flat=True)
                if employee_groups:
                    error_group_text = ', '.join(employee_groups)
                    raise ParseError(
                        f'Невозможно сменить должность. Сотрудник является '
                        f'менеджером в следующих группах:  {error_group_text}.'
                    )
        return value


class EmployeeDeleteSerializer(serializers.Serializer):
    def validate(self, attrs):
        if self.instance.is_director:
            raise ParseError(
                'невозможно удалить руководителя из организации.'
            )
        groups_as_member = self.instance.groups_members.values_list('name', flat=True)
        groups_as_manager = self.instance.groups_managers.values_list('name', flat=True)
        groups_exists = set(groups_as_member).union(set(groups_as_manager))
        if groups_exists:
            error_group_text = ', '.join(list(groups_exists))
            raise ParseError(
                f'Удаление невозможно. Сотрудник находится в следующих группах '
                f'менеджером в следующих группах:  {error_group_text}.'
            )

        return attrs
