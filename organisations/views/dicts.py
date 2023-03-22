from drf_spectacular.utils import extend_schema, extend_schema_view

from common.views.mixins import DictListMixin
from organisations.models.dicts import Position


@extend_schema_view(
    list=extend_schema(summary='Список должностей', tags=['Словари']),
)
class PositionView(DictListMixin):
    model = Position
