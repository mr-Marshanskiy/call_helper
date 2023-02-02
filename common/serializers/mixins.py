from rest_framework import serializers

from users.serializers.nested.users import UserShortSerializer


class ExtendedModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True


class InfoModelSerializer(ExtendedModelSerializer):
    created_by = UserShortSerializer()
    updated_by = UserShortSerializer()

    class Meta:
        abstract = True


class DictMixinSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()


