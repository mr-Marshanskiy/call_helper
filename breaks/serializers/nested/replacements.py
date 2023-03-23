import datetime

from rest_framework import serializers

from breaks.models.replacements import (GroupInfo, Replacement,
                                        ReplacementMember)
from common.serializers.mixins import (DictMixinSerializer,
                                       ExtendedModelSerializer,
                                       InfoModelSerializer)
from common.services import convert_timedelta_to_str_time


class BreakSettingsSerializer(ExtendedModelSerializer):
    class Meta:
        model = GroupInfo
        exclude = ('group',)


class ReplacementShortSerializer(InfoModelSerializer):

    class Meta:
        model = Replacement
        fields = (
            'id',
            'date',
            'break_start',
            'break_end',
            'break_max_duration',
            'min_active',
        )


class ReplacementMemberShortSerializer(ExtendedModelSerializer):
    id = serializers.CharField(source='member.employee.user.pk')
    full_name = serializers.CharField(source='member.employee.user.full_name')
    username = serializers.CharField(source='member.employee.user.username')
    email = serializers.CharField(source='member.employee.user.email')
    description = serializers.SerializerMethodField()
    status = DictMixinSerializer()

    class Meta:
        model = ReplacementMember
        fields = (
            'id',
            'full_name',
            'username',
            'email',
            'status',
            'description',
        )

    def get_description(self, instance):
        if not instance.break_start:
            return None

        now = datetime.datetime.now().astimezone()
        break_start = datetime.datetime.combine(now.date(), instance.break_start).astimezone()
        break_end = datetime.datetime.combine(now.date(), instance.break_end).astimezone()

        if break_start > now:
            delta = break_start - now
            return f'Обед начнется через {convert_timedelta_to_str_time(delta)}'
        elif break_end > now:
            delta = break_end - now
            return f'Обед закончится через {convert_timedelta_to_str_time(delta)}'

        return None
