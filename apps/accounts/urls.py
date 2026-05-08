from django.urls import path

from apps.accounts.views import (
    # UpdateUserEmailView
    UserView, UpdateUserPasswordView,
    EmailConfirmView,
)


urlpatterns = [
    path(
        '', UserView.as_view({'get': 'list', 'post': 'create'}),
        name='user_registration'
    ),
    path(
        'password/', UpdateUserPasswordView.as_view(),
        name='change_password'
    ),
    path(
        '<int:pk>/', UserView.as_view({'get': 'retrieve'}),
        name='user_info'
    ),
    # path(
    #     'emails/', UpdateUserEmailView.as_view(),
    #     name='add_email'
    # ),
    path(
        'email/confirm/', EmailConfirmView.as_view(),
        name='confirmed_email'
    ),
]
