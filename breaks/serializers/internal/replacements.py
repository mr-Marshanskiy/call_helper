import datetime

from crum import get_current_user
from django.utils import timezone
from rest_framework import serializers

from breaks.models.replacements import Replacement, ReplacementMember
from breaks.serializers.internal.breaks import BreakForReplacementSerializer
from common.serializers.mixins import ExtendedModelSerializer
from organisations.serializers.nested.groups import GroupShortSerializer


class ReplacementGeneralSerializer(ExtendedModelSerializer):
    group = GroupShortSerializer(source='group.group')
    break_start = serializers.TimeField(format='%H:%M')
    break_end = serializers.TimeField(format='%H:%M')
    date = serializers.DateField(format='%d.%m.%Y')

    class Meta:
        model = Replacement
        fields = (
            'id',
            'group',
            'date',
            'break_start',
            'break_end',
            'break_max_duration',
            'min_active',
        )


class ReplacementPersonalStatsSerializer(ExtendedModelSerializer):
    time_online = serializers.DateTimeField(format='%H:%M')
    time_break_start = serializers.DateTimeField(format='%H:%M')
    time_break_end = serializers.DateTimeField(format='%H:%M')
    time_offline = serializers.DateTimeField(format='%H:%M')
    time_until_break = serializers.SerializerMethodField()

    class Meta:
        model = ReplacementMember
        fields = (
            'time_online',
            'time_break_start',
            'time_break_end',
            'time_offline',
            'time_until_break',
        )

    @property
    def data(self):
        data = super().data
        if 'time_until_break' not in data:
            data['time_until_break'] = None
        return data

    def get_time_until_break(self, instance):
        if not instance:
            return None
        break_obj = instance.breaks.filter(replacement=instance.replacement).first()
        if not break_obj:
            return None

        now = datetime.datetime.now().time()
        now_minutes = now.hour * 60 + now.minute
        break_minutes = break_obj.break_start.hour * 60 + break_obj.break_start.minute

        delta = break_minutes - now_minutes

        if delta < 0:
            return None

        delta_hours = delta // 60
        delta_minutes = delta % 60
        result = f'{delta_hours // 10}{delta_hours % 10}:{delta_minutes // 10}{delta_minutes % 10}'
        return result


class ReplacementBreakSerializer(serializers.Serializer):
    info = serializers.SerializerMethodField()
    button = serializers.SerializerMethodField()

    def get_info(self, instance):
        user = get_current_user()
        break_obj = instance.get_break_for_user(user)
        return BreakForReplacementSerializer(break_obj, allow_null=True).data

    def get_button(self, instance):
        user = get_current_user()
        return instance.get_break_status_for_user(user)


class ReplacementActionSerializer(serializers.Serializer):
    replacement_button = serializers.SerializerMethodField()
    break_button = serializers.SerializerMethodField()

    def get_replacement_button(self, instance):
        now = timezone.now().astimezone()
        if instance.date != now.date():
            return None
        user = get_current_user()
        member = instance.get_member_by_user(user)
        if not member:
            return None

    def get_button(self, instance):
        user = get_current_user()
        return instance.get_break_status_for_user(user)
