from breaks.models.replacements import GroupInfo, Replacement
from common.serializers.mixins import ExtendedModelSerializer, \
    InfoModelSerializer


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