from django.urls import path, include
from rest_framework.routers import DefaultRouter

from breaks.views import dicts, replacements

router = DefaultRouter()

router.register(r'replacements', replacements.ReplacementView, 'replacements')
router.register(r'dicts/statuses/breaks', dicts.BreakStatusView, 'breaks-statuses')
router.register(r'dicts/statuses/replacements', dicts.ReplacementStatusView, 'replacement-statuses')

urlpatterns = [
    path('breaks/replacements/<int:pk>/member/', replacements.MeReplacementMemberView.as_view(), name='replacement-member'),

    path('breaks/', include(router.urls)),
]

