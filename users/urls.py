from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import users

router = DefaultRouter()


router.register(r'search', users.UserListSearchView, 'users-search')

urlpatterns = [
    path('users/reg/', users.RegistrationView.as_view(), name='reg'),
    path('users/me/', users.MeView.as_view(), name='me'),
    path('users/change-passwd/', users.ChangePasswordView.as_view(), name='change_passwd'),
]

urlpatterns += path('users/', include(router.urls)),
