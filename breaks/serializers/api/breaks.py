from crum import get_current_user
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from breaks.models.breaks import Break
from breaks.models.replacements import Replacement, ReplacementMember
from breaks.serializers.nested.replacements import ReplacementShortSerializer
from common.serializers.mixins import InfoModelSerializer, DictMixinSerializer

User = get_user_model()


class BreakMeRetrieveSerializer(InfoModelSerializer):
    status = DictMixinSerializer()
    replacement = ReplacementShortSerializer()

    class Meta:
        model = Break
        fields = (
            'id',
            'replacement',
            'break_start',
            'break_end',
            'status',
        )


class BreakMeCreateSerializer(InfoModelSerializer):

    class Meta:
        model = Break
        fields = (
            'id',
            'break_start',
            'break_end',
        )

    def validate(self, attrs):
        replacement = self.get_object_from_url(Replacement)
        user = get_current_user()

        member = ReplacementMember.objects.filter(
            replacement=replacement,
            member__employee__user=user
        ).first()

        if not member:
            raise ParseError('У вас нет доступа к текущей смене.')

        attrs['replacement'] = replacement
        attrs['member'] = member
        return attrs


class BreakMeUpdateSerializer(InfoModelSerializer):

    class Meta:
        model = Break
        fields = (
            'id',
            'break_start',
            'break_end',
        )
