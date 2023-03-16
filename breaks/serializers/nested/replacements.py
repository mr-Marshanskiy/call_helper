from rest_framework import serializers

from breaks.models.replacements import GroupInfo, Replacement, ReplacementMember
from common.serializers.mixins import ExtendedModelSerializer, \
    InfoModelSerializer, DictMixinSerializer


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
    status = DictMixinSerializer()

    class Meta:
        model = ReplacementMember
        fields = (
            'id',
            'full_name',
            'username',
            'email',
            'status',
        )
