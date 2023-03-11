import pdb

from django.db.models import Q
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import get_object_or_404

from breaks.models.breaks import Break
from common.views.mixins import ExtendedCRUAPIView, ListViewSet
from breaks.serializers.api import breaks as breaks_s


@extend_schema_view(
    get=extend_schema(summary='Деталка обеда', tags=['Обеды: Обеды пользователя']),
    post=extend_schema(summary='Резерв обеда', tags=['Обеды: Обеды пользователя']),
    put=extend_schema(summary='Измемение резерва обеда', tags=['Обеды: Обеды пользователя']),
)
class BreakMeView(ExtendedCRUAPIView):
    # permission_classes = [IsNotCorporate]
    queryset = Break.objects.all()
    serializer_class = breaks_s.BreakMeUpdateSerializer
    multi_serializer_class = {
        'GET': breaks_s.BreakMeRetrieveSerializer,
    }
    http_method_names = ('get', 'post', 'put')

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

    def get_queryset(self):
        replacement_id = self.request.parser_context['kwargs'].get('pk')
        return Break.objects.prefetch_related(
            'member',
            'member__member',
            'member__member__employee',
            'member__member__employee__user',
        ).filter(replacement_id=replacement_id)
