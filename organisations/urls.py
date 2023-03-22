from django.urls import include, path
from rest_framework.routers import DefaultRouter

from organisations.views import (dicts, employees, groups, members, offers,
                                 organisations)

router = DefaultRouter()

router.register(r'dicts/positions', dicts.PositionView, 'positions')
router.register(r'search', organisations.OrganisationSearchView, 'organisations-search')
router.register(r'(?P<pk>\d+)/employees', employees.EmployeeView, 'employees')
router.register(r'offers', offers.OfferUserView, 'user-offers')
router.register(r'(?P<pk>\d+)/offers', offers.OfferOrganisationView, 'org-offers')
router.register(r'groups/(?P<pk>\d+)/members', members.MemberView, 'members')
router.register(r'groups', groups.GroupView, 'groups')
router.register(r'', organisations.OrganisationView, 'organisations')

urlpatterns = [
    path('organisations/', include(router.urls)),
]
