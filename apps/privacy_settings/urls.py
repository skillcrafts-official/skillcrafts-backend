"""The url routing for app $PATH_TO_APP"""
from django.urls import path

from apps.privacy_settings.views import (
    ProfilePrivacySettingsView,
    ProfileUserBlacklistView, ProfileUserWhitelistView
    # ProfileGetPrivacySettingsView, ProfileSetPrivacySettingsView
)


urlpatterns = [
    path(
        'my-profile/privacies/',
        ProfilePrivacySettingsView.as_view({
            'get': 'retrieve', 'patch': 'partial_update'
        }),
        name='get_or_update_profile_privacy_settings'
    ),
    # path(
    #     'profiles/<int:pk>/privacy/update',
    #     UpdateProfilePrivacySettingsView.as_view({'patch': 'update'}),
    #     name='update_profile_privacy_settings'
    # ),
    path(
        'my-profile/blacklist/',
        ProfileUserBlacklistView.as_view({'patch': 'update'}),
        name='profile_user_blacklist'
    ),
    path(
        'my-profile/whitelist/',
        ProfileUserWhitelistView.as_view({'patch': 'update'}),
        name='profile_user_whitelist'
    ),
]
