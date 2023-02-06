from django.db.models import Count, Case, When, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.filters import SearchFilter, OrderingFilter

from common.views.mixins import CRUViewSet
from organisations.backends import MyOrganisation, MyGroup
from organisations.filters import GroupFilter
from organisations.models.groups import Group
from organisations.permissions import IsColleagues, IsMyGroup
from organisations.serializers.api import groups as groups_s


@extend_schema_view(
    list=extend_schema(summary='Список групп', tags=['Организации: Группы']),
    retrieve=extend_schema(summary='Деталка группы', tags=['Организации: Группы']),
    create=extend_schema(summary='Создать группу', tags=['Организации: Группы']),
    update=extend_schema(summary='Изменить группу', tags=['Организации: Группы']),
    partial_update=extend_schema(summary='Изменить группу частично', tags=['Организации: Группы']),
)
class GroupView(CRUViewSet):
    permission_classes = [IsMyGroup]

    queryset = Group.objects.all()
    serializer_class = groups_s.GroupListSerializer

    multi_serializer_class = {
        'list': groups_s.GroupListSerializer,
        'retrieve': groups_s.GroupRetrieveSerializer,
        'create': groups_s.GroupCreateSerializer,
        'update': groups_s.GroupUpdateSerializer,
        'partial_update': groups_s.GroupUpdateSerializer,
    }

    http_method_names = ('get', 'post', 'patch')

    filter_backends = (
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
        MyGroup,
    )
    search_fields = ('name',)
    filterset_class = GroupFilter
    ordering = ('name', 'id',)

    def get_queryset(self):
        queryset = Group.objects.select_related(
            'manager',
        ).prefetch_related(
            'organisation',
            'organisation__director',
            'members',
        ).annotate(
            pax=Count('members', distinct=True),
            can_manage=Case(
                When(
                    Q(manager__user=self.request.user) |
                    Q(organisation__director=self.request.user),
                    then=True
                ),
                default=False,
            ),
            is_member=Case(
                When(Q(members_info__employee__user=self.request.user), then=True),
                default=False,
            ),
        )
        return queryset
