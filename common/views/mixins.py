from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from common.serializers.mixins import DictMixinSerializer


class ExtendedGenericViewSet(GenericViewSet):
    pass


class ListViewSet(ExtendedGenericViewSet, mixins.ListModelMixin):
    pass


class DictListMixin(ListViewSet):
    serializer_class = DictMixinSerializer
    pagination_class = None


class CRUViewSet(ExtendedGenericViewSet,
                 mixins.CreateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.ListModelMixin,):
    pass


class CRUDViewSet(CRUViewSet,
                  mixins.DestroyModelMixin,):
    pass

