from django.db.models import Case, Count, When
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter, SearchFilter

from common.views.mixins import LCRUViewSet, ListViewSet
from organisations.backends import MyOrganisation
from organisations.filters import OrganisationFilter
from organisations.models.organisations import Organisation
from organisations.permissions import IsMyOrganisation
from organisations.serializers.api import organisations


@extend_schema_view(
    list=extend_schema(summary='Список организаций Search', tags=['Словари']),
)
class OrganisationSearchView(ListViewSet):
    queryset = Organisation.objects.all()
    serializer_class = organisations.OrganisationSearchListSerializer


@extend_schema_view(
    list=extend_schema(summary='Список организаций', tags=['Организации']),
    retrieve=extend_schema(summary='Деталка организации', tags=['Организации']),
    create=extend_schema(summary='Создать организацию', tags=['Организации']),
    update=extend_schema(summary='Изменить организацию', tags=['Организации']),
    partial_update=extend_schema(summary='Изменить организацию частично', tags=['Организации']),
)
class OrganisationView(LCRUViewSet):
    permission_classes = [IsMyOrganisation]
    queryset = Organisation.objects.all()
    serializer_class = organisations.OrganisationListSerializer

    multi_serializer_class = {
        'list': organisations.OrganisationListSerializer,
        'retrieve': organisations.OrganisationRetrieveSerializer,
        'create': organisations.OrganisationCreateSerializer,
        'update': organisations.OrganisationUpdateSerializer,
        'partial_update': organisations.OrganisationUpdateSerializer,
    }

    http_method_names = ('get', 'post', 'patch')

    filter_backends = (
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
        MyOrganisation,
    )
    filterset_class = OrganisationFilter
    ordering = ('name', 'id',)

    def get_queryset(self):
        queryset = Organisation.objects.select_related(
            'director',
        ).annotate(
            pax=Count('employees', distinct=True),
            groups_count=Count('groups', distinct=True),
            can_manage=Case(
                When(director=self.request.user, then=True),
                default=False,
            )
        )
        return queryset
