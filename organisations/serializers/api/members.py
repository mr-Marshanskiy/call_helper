from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from common.serializers.mixins import ExtendedModelSerializer

from organisations.models.groups import Member, Group
from organisations.models.organisations import Employee
from organisations.serializers.nested.dicts import PositionShortSerializer
from organisations.serializers.nested.employees import EmployeeShortSerializer

User = get_user_model()


class MemberSearchSerializer(ExtendedModelSerializer):
    full_name = serializers.CharField(source='employee.user.full_name')
    username = serializers.CharField(source='employee.user.username')
    position = PositionShortSerializer(source='employee.position')

    class Meta:
        model = Member
        fields = (
            'id',
            'full_name',
            'username',
            'position',
        )


class MemberListSerializer(ExtendedModelSerializer):
    employee = EmployeeShortSerializer()

    class Meta:
        model = Member
        fields = (
            'id',
            'employee',
            'date_joined',
        )


class MemberRetrieveSerializer(ExtendedModelSerializer):
    employee = EmployeeShortSerializer()

    class Meta:
        model = Member
        fields = (
            'id',
            'employee',
            'date_joined',
        )


class MemberCreateSerializer(ExtendedModelSerializer):
    employees = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Member
        fields = (
            'id',
            'employees',
        )

    def validate(self, attrs):
        try:
            group = self.get_object_from_url(Group)
            organisation = group.organisation
        except:
            raise ParseError('Ой, что-то не так. Текущая организация не найдена.')

        attrs['group'] = group

        employees = attrs['employees']
        employees_id_set = {obj.pk for obj in employees}

        org_employees = organisation.employees_info.all()
        org_employees_id_set = {obj.pk for obj in org_employees}

        # Check employees from request exist in org
        if employees_id_set - org_employees_id_set:
            raise ParseError(
                'Некоторые из указанных сотрдуников не существуют в организации. '
                'Проверьте введенные данные.'
            )

        return attrs

    def create(self, validated_data):
        employees = validated_data.pop('employees')
        group = validated_data.pop('group')
        group.members.set(employees)
        return group
