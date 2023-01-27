from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import users

# router = DefaultRouter()


# router.register(r'reg', users.RegistrationView, 'reg')

urlpatterns = [
    path('users/reg/', users.RegistrationView.as_view(), name='reg')
]

# urlpatterns += path('users/', include(router.urls))
