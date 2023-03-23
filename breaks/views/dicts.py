from drf_spectacular.utils import extend_schema, extend_schema_view

from breaks.models.dicts import ReplacementStatus
from common.views.mixins import DictListMixin


@extend_schema_view(
    list=extend_schema(summary='Список статусов смен', tags=['Словари']),
)
class ReplacementStatusView(DictListMixin):
    model = ReplacementStatus
