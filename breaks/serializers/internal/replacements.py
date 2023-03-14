from rest_framework import serializers

from breaks.models.replacements import ReplacementMember
from common.serializers.mixins import InfoModelSerializer, \
    ExtendedModelSerializer


class ReplacementStatsSerializer(serializers.Serializer):
    all_pax = serializers.IntegerField()
    created_pax = serializers.IntegerField()
    confirmed_pax = serializers.IntegerField()
    on_break_pax = serializers.IntegerField()
    finished_pax = serializers.IntegerField()
    cancelled_pax = serializers.IntegerField()


class ReplacementPersonalStatsSerializer(ExtendedModelSerializer):
    class Meta:
        model = ReplacementMember
        fields = (
            'time_online',
            'time_break_start',
            'time_break_end',
            'time_offline',
        )
