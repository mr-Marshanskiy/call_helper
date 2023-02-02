from django.db.models import Count, Case, When
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.filters import SearchFilter, OrderingFilter

from common.views.mixins import ListViewSet, CRUViewSet
from organisations.backends import MyOrganisation
from organisations.filters import OrganisationFilter
from organisations.models.organisations import Organisation
from organisations.permissions import IsOwner
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
class OrganisationView(CRUViewSet):
    queryset = Organisation.objects.all()
    serializer_class = organisations.OrganisationListSerializer

    multi_permission_classes = {
        'update': [IsOwner],
        'partial_update': [IsOwner]
    }
    multi_serializer_class = {
        'list': organisations.OrganisationListSerializer,
        'retrieve': organisations.OrganisationRetrieveSerializer,
        'create': organisations.OrganisationCreateSerializer,
        'update': organisations.OrganisationUpdateSerializer,
        'partial_update': organisations.OrganisationUpdateSerializer,
    }

    filter_backends = [
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
        MyOrganisation,
    ]
    http_method_names = ['get', 'post', 'patch']
    search_fields = ('name',)
    filterset_class = OrganisationFilter
    ordering = ('name', 'id',)

    def get_queryset(self):
        queryset = Organisation.objects.select_related(
            'director',
        ).prefetch_related(
            'employees',
            'groups',
        ).annotate(
            pax=Count('employees', distinct=True),
            groups_count=Count('groups', distinct=True),
            can_manage=Case(
                When(created_by=self.request.user, then=True),
                default=False,
            )
        )
        return queryset
