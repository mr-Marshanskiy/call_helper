from django.contrib.auth import get_user_model
from rest_framework import serializers

from breaks.models.replacements import Replacement
from breaks.serializers.internal.replacements import ReplacementStatsSerializer
from common.serializers.mixins import InfoModelSerializer

User = get_user_model()


class ReplacementListSerializer(InfoModelSerializer):
    all_pax = serializers.IntegerField()
    stats = ReplacementStatsSerializer(source='*')

    class Meta:
        model = Replacement
        fields = '__all__'


class ReplacementRetrieveSerializer(InfoModelSerializer):
    class Meta:
        model = Replacement
        fields = '__all__'


class ReplacementCreateSerializer(InfoModelSerializer):
    class Meta:
        model = Replacement
        fields = '__all__'


class ReplacementUpdateSerializer(InfoModelSerializer):
    class Meta:
        model = Replacement
        fields = '__all__'
