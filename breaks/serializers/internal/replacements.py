from rest_framework import serializers


class ReplacementStatsSerializer(serializers.Serializer):
    all_pax = serializers.IntegerField()
    created_pax = serializers.IntegerField()
    confirmed_pax = serializers.IntegerField()
    on_break_pax = serializers.IntegerField()
    finished_pax = serializers.IntegerField()
    cancelled_pax = serializers.IntegerField()
