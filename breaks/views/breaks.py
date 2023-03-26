from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from breaks.models.breaks import Break
from breaks.models.replacements import Replacement
from breaks.serializers.api import breaks as breaks_s
from common.services import get_schedule_time_title
from common.views.mixins import ExtendedCRUAPIView, ListViewSet


@extend_schema_view(
    get=extend_schema(summary='Деталка обеда', tags=['Обеды: Обеды пользователя']),
    post=extend_schema(summary='Резерв обеда', tags=['Обеды: Обеды пользователя']),
    patch=extend_schema(summary='Измемение резерва обеда', tags=['Обеды: Обеды пользователя']),
)
class BreakMeView(ExtendedCRUAPIView):
    # permission_classes = [IsNotCorporate]
    queryset = Break.objects.all()
    serializer_class = breaks_s.BreakMeUpdateSerializer
    multi_serializer_class = {
        'GET': breaks_s.BreakMeRetrieveSerializer,
    }
    http_method_names = ('get', 'post', 'patch')

    def get_object(self):
        user = self.request.user
        replacement_id = self.request.parser_context['kwargs'].get('pk')

        return get_object_or_404(
            Break, Q(replacement_id=replacement_id, member__member__employee__user=user)
        )


@extend_schema_view(
    list=extend_schema(summary='Расписание обедов', tags=['Обеды: Обеды']),
)
class BreakScheduleView(ListViewSet):
    # permission_classes = [IsNotCorporate]
    queryset = Break.objects.all()
    serializer_class = breaks_s.BreakScheduleSerializer
    pagination_class = None

    def list(self, request, *args, **kwargs):
        replacement_id = self.request.parser_context['kwargs'].get('pk')
        replacement = get_object_or_404(Replacement, id=replacement_id)
        title = get_schedule_time_title(
            replacement.break_start, replacement.break_end, 'Сотрудник'
        )
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True).data
        serializer.insert(0, title)
        return Response(serializer)

    def get_queryset(self):
        replacement_id = self.request.parser_context['kwargs'].get('pk')
        return Break.objects.prefetch_related(
            'member',
            'member__member',
            'member__member__employee',
            'member__member__employee__user',
        ).filter(replacement_id=replacement_id)
