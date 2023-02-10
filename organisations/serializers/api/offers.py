import pdb

from crum import get_current_user
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from common.serializers.mixins import ExtendedModelSerializer, \
    InfoModelSerializer
from organisations.cinstants import OPERATOR_POSITION
from organisations.models.offers import Offer
from organisations.models.organisations import Organisation
from organisations.serializers.nested.organisations import \
    OrganisationShortSerializer
from users.serializers.nested.users import UserShortSerializer


User = get_user_model()


# From Org to User
class OfferOrgToUserListSerializer(InfoModelSerializer):
    user = UserShortSerializer()
    can_accept = serializers.BooleanField()
    can_reject = serializers.BooleanField()

    class Meta:
        model = Offer
        fields = (
            'id',
            'org_accept',
            'user',
            'user_accept',
            'created_at',
            'updated_at',
            'can_accept',
            'can_reject',
        )


class OfferOrgToUserCreateSerializer(ExtendedModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.exclude(is_corporate_account=True), many=True,
        write_only=True,
    )

    class Meta:
        model = Offer
        fields = (
            'users',
        )

    def validate(self, attrs):
        users = attrs['users']
        organisation = self.get_object_from_url(Organisation)
        attrs['organisation'] = organisation
        attrs['org_accept'] = True

        # check offer create already
        offers_exist = self.Meta.model.objects.filter(
            user__in=users,
            organisation=organisation,
        )
        if offers_exist:
            user_error = '\n'.join(
                [f'{offer.user.full_name} ({offer.user.email})' for offer in offers_exist]
            )
            raise ParseError(
                f'Следующие пользователи уже были приглашены ранее:\n'
                f'{user_error}'
            )
        # check user in org already
        users_in_orgs = organisation.employees_info.filter(user__in=users)
        if users_in_orgs:
            user_error = '\n'.join([employee.user.full_name for employee in users_in_orgs])
            raise ParseError(
                f'Следующие пользователи уже в Вашей компании:\n'
                f'{user_error}'
            )
        return attrs

    def create(self, validated_data):
        users = validated_data.pop('users')
        with transaction.atomic():
            for user in users:
                validated_data['user'] = user
                instance = super().create(validated_data)
        return instance


class OfferOrgToUserUpdateSerializer(ExtendedModelSerializer):
    accept = serializers.BooleanField(write_only=True)

    class Meta:
        model = Offer
        fields = (
            'id',
            'accept',
        )

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['org_accept'] = data.pop('accept')
        return data

    def validate(self, attrs):
        # Offer from org to user
        if self.instance.is_from_org:
            if self.instance.user_accept is not None:
                raise ParseError(
                    'Заявка закрыта. Изменение недоступно.'
                )
        else:
            # Offer from user to org
            if self.instance.org_accept is not None:
                raise ParseError(
                    'Заявка закрыта. Изменение недоступно.'
                )
        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = super().update(instance, validated_data)

            # Create employee
            if instance.user_accept and instance.org_accept:
                instance.organisation.employees.add(
                    instance.user,
                    through_defaults={'position_id': OPERATOR_POSITION, }
                )
        return instance


# From User to Org
class OfferUserToOrgListSerializer(InfoModelSerializer):
    organisation = OrganisationShortSerializer()
    can_accept = serializers.BooleanField()
    can_reject = serializers.BooleanField()

    class Meta:
        model = Offer
        fields = (
            'id',
            'organisation',
            'org_accept',
            'user_accept',
            'created_at',
            'updated_at',
            'can_accept',
            'can_reject',
        )


class OfferUserToOrgCreateSerializer(ExtendedModelSerializer):

    class Meta:
        model = Offer
        fields = (
            'id',
            'organisation',
        )

    def validate(self, attrs):
        user = get_current_user()
        organisation = attrs['organisation']
        attrs['organisation'] = organisation
        attrs['user_accept'] = True
        attrs['user'] = user

        # check offer create already
        offer_exist = self.Meta.model.objects.filter(
            organisation=organisation,
            user=user,
        ).exists()
        if offer_exist:
            raise ParseError(f'Заявка в эту организацию была отправлена ранее.')

        # check user in org already
        already_in_org = organisation.employees_info.filter(user=user).exists()
        if already_in_org:
            raise ParseError(
                f'Вы уже являетесь сотрудником организации.'
            )
        return attrs


class OfferUserToOrgUpdateSerializer(ExtendedModelSerializer):
    accept = serializers.BooleanField(write_only=True)

    class Meta:
        model = Offer
        fields = (
            'id',
            'accept',
        )

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['user_accept'] = data.pop('accept')
        return data

    def validate(self, attrs):
        # Offer from user to org
        if self.instance.is_from_user:
            if self.instance.org_accept is not None:
                raise ParseError(
                    'Заявка закрыта. Изменение недоступно.'
                )
        else:
            # Offer from org to user
            if self.instance.user_accept is not None:
                raise ParseError(
                    'Заявка закрыта. Изменение недоступно.'
                )
        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = super().update(instance, validated_data)

            # Create employee
            if instance.user_accept and instance.org_accept:
                instance.organisation.employees.add(
                    instance.user,
                    through_defaults={'position_id': OPERATOR_POSITION, }
                )
        return instance
