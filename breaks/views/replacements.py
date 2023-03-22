from crum import get_current_user
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404

from breaks.factory.replacements import ReplacementFactory
from breaks.filters import ReplacementFilter
from breaks.models.replacements import Replacement, ReplacementMember
from breaks.serializers.api import replacements as replacements_s
from common.views.mixins import ExtendedRetrieveUpdateAPIView, LCRUViewSet


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
    )
    filterset_class = ReplacementFilter

    def get_queryset(self):
        return ReplacementFactory().list()


@extend_schema_view(
    get=extend_schema(summary='Данные участника смены', tags=['Обеды: Смены']),
    patch=extend_schema(summary='Изменить участника смены', tags=['Обеды: Смены']),
)
class MeReplacementMemberView(ExtendedRetrieveUpdateAPIView):
    queryset = ReplacementMember.objects.all()
    serializer_class = replacements_s.ReplacementMemberListSerializer
    multi_serializer_class = {
        'GET': replacements_s.ReplacementMemberListSerializer,
        'PATCH': replacements_s.ReplacementMemberUpdateSerializer,
    }

    def get_object(self):
        user = get_current_user()
        replacement_id = self.request.parser_context['kwargs'].get('pk')
        member = get_object_or_404(
            ReplacementMember,
            Q(replacement_id=replacement_id, member__employee__user=user)
        )
        return member
