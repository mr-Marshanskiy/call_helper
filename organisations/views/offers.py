from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter

from common.views.mixins import LCUViewSet
from organisations.backends import OwnedByOrganisation
from organisations.factory.offers import OfferFactory
from organisations.filters import OfferOrgFilter, OfferUserFilter
from organisations.models.offers import Offer
from organisations.permissions import IsOfferManager
from organisations.serializers.api import offers as offers_s


@extend_schema_view(
    list=extend_schema(summary='Список офферов организации', tags=['Организации: Офферы']),
    create=extend_schema(summary='Создать ооферы пользователям', tags=['Организации: Офферы']),
    partial_update=extend_schema(summary='Изменить оффер пользователя частично', tags=['Организации: Офферы']),
)
class OfferOrganisationView(LCUViewSet):
    permission_classes = [IsOfferManager]

    queryset = Offer.objects.all()
    serializer_class = offers_s.OfferOrgToUserListSerializer

    multi_serializer_class = {
        'list': offers_s.OfferOrgToUserListSerializer,
        'create': offers_s.OfferOrgToUserCreateSerializer,
        'partial_update': offers_s.OfferOrgToUserUpdateSerializer,
    }

    lookup_url_kwarg = 'offer_id'
    http_method_names = ('get', 'post', 'patch',)

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        OwnedByOrganisation,
    )
    filterset_class = OfferOrgFilter
    ordering_fields = ('-created_at', 'updated_at',)

    def get_queryset(self):
        return OfferFactory().org_list()


@extend_schema_view(
    list=extend_schema(summary='Список офферов пользователя', tags=['Организации: Офферы']),
    create=extend_schema(summary='Создать оофер в организацию', tags=['Организации: Офферы']),
    partial_update=extend_schema(summary='Изменить оффер в организацию частично', tags=['Организации: Офферы']),
)
class OfferUserView(LCUViewSet):
    queryset = Offer.objects.all()
    serializer_class = offers_s.OfferUserToOrgListSerializer

    multi_serializer_class = {
        'list': offers_s.OfferUserToOrgListSerializer,
        'create': offers_s.OfferUserToOrgCreateSerializer,
        'partial_update': offers_s.OfferUserToOrgUpdateSerializer,
    }

    http_method_names = ('get', 'post', 'patch',)

    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
    )
    filterset_class = OfferUserFilter
    ordering_fields = ('created_at', 'updated_at',)

    def get_queryset(self):
        return OfferFactory().user_list()
