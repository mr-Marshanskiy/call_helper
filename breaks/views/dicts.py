from drf_spectacular.utils import extend_schema, extend_schema_view

from breaks.models.dicts import BreakStatus, ReplacementStatus
from common.views.mixins import DictListMixin


@extend_schema_view(
    list=extend_schema(summary='Список статусов смен', tags=['Словари']),
)
class ReplacementStatusView(DictListMixin):
    model = ReplacementStatus


@extend_schema_view(
    list=extend_schema(summary='Список статусов обеденных перерывов', tags=['Словари']),
)
class BreakStatusView(DictListMixin):
    model = BreakStatus
