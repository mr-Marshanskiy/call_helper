from common.serializers.mixins import DictMixinSerializer
from organisations.models.dicts import Position


class PositionShortSerializer(DictMixinSerializer):
    class Meta:
        model = Position
