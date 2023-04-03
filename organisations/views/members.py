from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action

from common.views.mixins import LCDViewSet
from organisations.backends import OwnedByGroup
from organisations.models.groups import Member
from organisations.permissions import IsMembers
from organisations.serializers.api import members as members_s


@extend_schema_view(
    list=extend_schema(summary='Список участников группы', tags=['Организации: Группы: Участники']),
    create=extend_schema(summary='Создать участника группы', tags=['Организации: Группы: Участники']),
    destroy=extend_schema(summary='Удалить участника из группы', tags=['Организации: Группы: Участники']),
    search=extend_schema(filters=True, summary='Список участников группы Search', tags=['Словари']),
)
class MemberView(LCDViewSet):
    permission_classes = [IsMembers]

    queryset = Member.objects.all()
    serializer_class = members_s.MemberListSerializer

    multi_serializer_class = {
        'list': members_s.MemberListSerializer,
        'create': members_s.MemberCreateSerializer,
        'search': members_s.MemberSearchSerializer,
    }

    lookup_url_kwarg = 'member_id'

    filter_backends = (OwnedByGroup,)

    def get_queryset(self):
        qs = Member.objects.select_related(
            'employee',
        ).prefetch_related(
            'group',
            'employee__user',
            'employee__organisation',
            'employee__organisation',
            'employee__position',
        )
        return qs

    @action(methods=['GET'], detail=False, url_path='search')
    def search(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
