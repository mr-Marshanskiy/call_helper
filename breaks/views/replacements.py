from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.filters import OrderingFilter

from breaks.factory.replacements import ReplacementFactory
from breaks.models.replacements import Replacement
from common.views.mixins import LCRUViewSet
from breaks.serializers.api import replacements as replacements_s


@extend_schema_view(
    list=extend_schema(summary='Список смен', tags=['Обеды: Смены']),
    retrieve=extend_schema(summary='Деталка смены', tags=['Обеды: Смены']),
    create=extend_schema(summary='Создать смену', tags=['Обеды: Смены']),
    partial_update=extend_schema(summary='Изменить смену частично', tags=['Обеды: Смены']),
)
class ReplacementView(LCRUViewSet):
    # permission_classes = [IsMyReplacement]

    queryset = Replacement.objects.all()
    serializer_class = replacements_s.ReplacementListSerializer

    multi_serializer_class = {
        'list': replacements_s.ReplacementListSerializer,
        'retrieve': replacements_s.ReplacementRetrieveSerializer,
        'create': replacements_s.ReplacementCreateSerializer,
        'partial_update': replacements_s.ReplacementUpdateSerializer,
    }

    http_method_names = ('get', 'post', 'patch')

    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
        # MyReplacement,
    )
    # filterset_class = ReplacementFilter

    def get_queryset(self):
        return ReplacementFactory().list()
