from django.urls import include, path

from api.spectacular.urls import urlpatterns as doc_urls
from breaks.urls import urlpatterns as breaks_urls
from organisations.urls import urlpatterns as organisation_urls
from users.urls import urlpatterns as user_urls

app_name = 'api'

urlpatterns = [
    path('auth/', include('djoser.urls.jwt')),
]

urlpatterns += doc_urls
urlpatterns += organisation_urls
urlpatterns += breaks_urls
urlpatterns += user_urls
