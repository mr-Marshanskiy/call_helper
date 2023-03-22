from breaks.models.breaks import Break
from common.serializers.mixins import ExtendedModelSerializer


class BreakForReplacementSerializer(ExtendedModelSerializer):
    class Meta:
        model = Break
        fields = (
            'id',
            'break_start',
            'break_end',
        )
        extra_kwargs = {
            'break_start': {'format': '%H:%M'},
            'break_end': {'format': '%H:%M'},
        }
