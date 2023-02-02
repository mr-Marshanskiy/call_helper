from django.urls import path, include
from rest_framework.routers import DefaultRouter

from organisations.views import dicts, organisations, employees

router = DefaultRouter()

router.register(r'dicts/positions', dicts.PositionView, 'positions')
router.register(r'search', organisations.OrganisationSearchView, 'organisations-search')
router.register(r'manage', organisations.OrganisationView, 'organisations')
router.register(r'manage/(?P<pk>\d+)/employees', employees.EmployeeView, 'employees')

urlpatterns = [
    path('organisations/', include(router.urls)),
]

