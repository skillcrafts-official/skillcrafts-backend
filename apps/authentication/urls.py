"""The urls routing for app auth"""

from django.urls import path

from .views import (
    # GuestTokenObtainView,
    MyTokenObtainPairView, MyTokenRefreshView, MyTokenVerifyView
)
from .authentication import UnifiedJWTAuthentication


urlpatterns = [
    path(
        'token/', MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'token/refresh/', MyTokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'token/verify/', MyTokenVerifyView.as_view(),
        name='token_verify'
    ),
    # path(
    #     'guest-token/', GuestTokenObtainView.as_view(),
    #     name='gest_token_obtain_pair'
    # ), обрезаем для первого релиза
]
