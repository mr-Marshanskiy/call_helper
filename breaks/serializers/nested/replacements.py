from breaks.models.replacements import GroupInfo
from common.serializers.mixins import ExtendedModelSerializer


class BreakSettingsSerializer(ExtendedModelSerializer):
    class Meta:
        model = GroupInfo
        exclude = ('group',)
