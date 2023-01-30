from drf_spectacular.utils import extend_schema_view, extend_schema

from common.views.mixins import DictListMixin
from organisations.models.dicts import Position


@extend_schema_view(
    list=extend_schema(summary='Список должностей', tags=['Словари']),
)
class PositionView(DictListMixin):
    queryset = Position.objects.filter(is_active=True)
