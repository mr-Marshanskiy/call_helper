from rest_framework import serializers


class ExtendedModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True


class DictMixinSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
