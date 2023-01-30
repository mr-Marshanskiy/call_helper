from django.urls import path, include
from rest_framework.routers import DefaultRouter

from organisations.views import dicts

router = DefaultRouter()

router.register(r'dicts/positions', dicts.PositionView, 'positions')

urlpatterns = [
    path('organisations/', include(router.urls)),
]

