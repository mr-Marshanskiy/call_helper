from drf_spectacular.utils import extend_schema_view, extend_schema

from common.views.mixins import CRUDViewSet
from organisations.backends import OwnedByOrganisation
from organisations.models.organisations import Employee
from organisations.serializers.api import employees as employees_s


@extend_schema_view(
    list=extend_schema(summary='Список сотрудников организации', tags=['Организации: Сотрудники']),
    retrieve=extend_schema(summary='Деталка сотрудника организации', tags=['Организации: Сотрудники']),
    create=extend_schema(summary='Создать сотрудника организации', tags=['Организации: Сотрудники']),
    update=extend_schema(summary='Изменить сотрудника организации', tags=['Организации: Сотрудники']),
    partial_update=extend_schema(summary='Изменить сотрудника организации частично', tags=['Организации: Сотрудники']),
    destroy=extend_schema(summary='Удалить сотрудника из организации', tags=['Организации: Сотрудники']),
)
class EmployeeView(CRUDViewSet):
    queryset = Employee.objects.all()
    serializer_class = employees_s.EmployeeListSerializer

    multi_serializer_class = {
        'list': employees_s.EmployeeListSerializer,
        'retrieve': employees_s.EmployeeRetrieveSerializer,
        'create': employees_s.EmployeeCreateSerializer,
        'update': employees_s.EmployeeUpdateSerializer,
        'partial_update': employees_s.EmployeeUpdateSerializer,
    }

    lookup_url_kwarg = 'employee_id'

    filter_backends = (
        OwnedByOrganisation,
    )


