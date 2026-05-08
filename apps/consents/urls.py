"""The urls routing for app consents"""

from django.urls import path

from apps.consents.views import UserConsentViewSet


urlpatterns = [
    path(
        'policy', UserConsentViewSet.as_view({'get': 'get_policy'}),
        name='privacy_policy'
    ),
    path(
        'personal', UserConsentViewSet.as_view({'get': 'get_personal'}),
        name='personal_data_processing'
    )
]
