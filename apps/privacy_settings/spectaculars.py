"""The DRF documentation extends for app ${PATH_TO_APP}"""
# pylint: disable=no-member,inherit-non-class,unnecessary-pass
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import (
    inline_serializer, extend_schema, extend_schema_view
)

from apps.privacy_settings.serializers import (
    ProfilePrivacySettingsSerializer, ProfileUserWhitelistSerializer,
    ProfileUserBlacklistSerializer
)
from apps.CONSTANTS import NOT_AUTHENTICATED, PERMISSION_DENIED, BAD_REQUEST
from docs.utils import read_md_section


class FixProfilePrivacySettingsView(OpenApiViewExtension):
    """
    Расширяется документация для ProfilePrivacySettingsView
    """
    target_class = 'apps.privacy_settings.views.ProfilePrivacySettingsView'

    def view_replacement(self) -> type[ModelViewSet]:
        @extend_schema_view(
            retrieve=extend_schema(
                summary="Получение настроек приватности профиля",
                description=read_md_section(
                    'api/privacy_settings.md',
                    'GET /privacy-settings/profiles/{profile}/privacies/'
                ),
                responses={
                    status.HTTP_200_OK: ProfilePrivacySettingsSerializer,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED,
                }
            ),
            partial_update=extend_schema(
                summary="Управление настройками конфиденциальности",
                description=read_md_section(
                    'api/privacy_settings.md',
                    'PATCH /privacy-settings/profiles/{profile}/privacies/'
                ),
                responses={
                    status.HTTP_200_OK: ProfilePrivacySettingsSerializer,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED,
                }
            )
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixProfileUserBlacklistView(OpenApiViewExtension):
    """
    Расширяется документация для ProfileUserBlacklistView
    """
    target_class = 'apps.privacy_settings.views.ProfileUserBlacklistView'

    def view_replacement(self) -> type[ModelViewSet]:
        @extend_schema_view(
            update=extend_schema(
                summary="Управление чёрным списком",
                description=read_md_section(
                    'api/privacy_settings.md',
                    'PATCH /privacy-settings/profiles/{profile}/blacklist/'
                ),
                responses={
                    status.HTTP_200_OK: ProfileUserBlacklistSerializer,
                    status.HTTP_400_BAD_REQUEST: BAD_REQUEST,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                }
            )
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixProfileUserWhitelistView(OpenApiViewExtension):
    """
    Расширяется документация для ProfileUserWhitelistView
    """
    target_class = 'apps.privacy_settings.views.ProfileUserWhitelistView'

    def view_replacement(self) -> type[ModelViewSet]:
        @extend_schema_view(
            update=extend_schema(
                summary="Управление белым списком",
                description=read_md_section(
                    'api/privacy_settings.md',
                    'PATCH /privacy-settings/profiles/{profile}/whitelist/'
                ),
                responses={
                    status.HTTP_200_OK: ProfileUserWhitelistSerializer,
                    status.HTTP_400_BAD_REQUEST: BAD_REQUEST,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                }
            )
        )
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed
