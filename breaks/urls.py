from django.urls import path, include
from rest_framework.routers import DefaultRouter

from breaks.views import dicts

router = DefaultRouter()

router.register(r'dicts/statuses/breaks', dicts.BreakStatusView, 'breaks-statuses')
router.register(r'dicts/statuses/replacements', dicts.ReplacementStatusView, 'replacement-statuses')

urlpatterns = [
    path('breaks/', include(router.urls)),
]

