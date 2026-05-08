"""The DRF documentation extends for app auth"""
# pylint: disable=no-member,inherit-non-class,unnecessary-pass
from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView

from drf_spectacular.utils import (
    inline_serializer, extend_schema, extend_schema_view,
)

from drf_spectacular.extensions import (
    OpenApiViewExtension, OpenApiAuthenticationExtension
)

from apps.CONSTANTS import BAD_REQUEST, NOT_AUTHENTICATED
from docs.utils import read_md_section


class UnifiedJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Расширение для drf-spectacular для поддержки UnifiedJWTAuthentication
    """
    target_class = 'apps.authentication.authentication.UnifiedJWTAuthentication'
    name = 'JWTAuth'  # Это имя должно совпадать с SECURITY_DEFINITIONS в настройках

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JWT Bearer Token для аутентификации пользователей и гостей'
        }


class FixMyTokenObtainPairView(OpenApiViewExtension):
    """
    Фиксирует расширение документации для MyTokenObtainPairView
    """
    target_class = 'apps.authentication.views.MyTokenObtainPairView'

    def view_replacement(self) -> type[GenericAPIView]:

        @extend_schema_view(
            post=extend_schema(
                summary="Получение JWT токенов для доступа к API",
                description=read_md_section('api/auth.md', 'POST /auth/token'),
                request=inline_serializer(
                    name='getJWT',
                    fields={
                        'email': serializers.EmailField(),
                        'password': serializers.CharField()
                    }
                ),
                responses={
                    status.HTTP_200_OK: inline_serializer(
                        name='JWT_response',
                        fields={
                            'refresh': serializers.CharField(
                                default='refresh_token...'
                            ),
                            'access': serializers.CharField(
                                default='access_token...'
                            ),
                            'user_id': serializers.IntegerField(),
                            'email': serializers.EmailField(),
                            'group': serializers.CharField(default='user'),
                        }
                    ),
                    status.HTTP_400_BAD_REQUEST: BAD_REQUEST,
                }
            )
        )
        # pylint: disable=missing-class-docstring
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixMyTokenRefreshView(OpenApiViewExtension):
    """
    Фиксирует расширение документации для MyTokenRefreshView
    """
    target_class = 'apps.authentication.views.MyTokenRefreshView'

    def view_replacement(self) -> type[GenericAPIView]:

        @extend_schema_view(
            post=extend_schema(
                summary="Получение Access Token",
                description=read_md_section('api/auth.md', 'POST /auth/token/refresh'),
                request=inline_serializer(
                    name='access_token_request',
                    fields={
                        'refresh': serializers.CharField(
                            default='refresh_token...'
                        ),
                    }
                ),
                responses={
                    status.HTTP_200_OK: inline_serializer(
                        name='access_token_response',
                        fields={
                            'refresh': serializers.CharField(
                                default='refresh_token...'
                            ),
                            'access': serializers.CharField(
                                default='access_token...'
                            ),
                        }
                    ),
                    status.HTTP_400_BAD_REQUEST: BAD_REQUEST,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                }
            )
        )
        # pylint: disable=missing-class-docstring
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixMyTokenVerifyView(OpenApiViewExtension):
    """
    Фиксирует расширение документации для MyTokenVerifyView
    """
    target_class = 'apps.authentication.views.MyTokenVerifyView'

    def view_replacement(self) -> type[GenericAPIView]:

        @extend_schema_view(
            post=extend_schema(
                summary="Верификация токенов",
                description=read_md_section('api/auth.md', 'POST /auth/token/verify'),
                request=inline_serializer(
                    name='verify_token_request',
                    fields={
                            'token': serializers.CharField(
                                default='refresh_or_access_token...'
                            ),
                        }
                ),
                responses={
                    status.HTTP_200_OK: {},
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                }
            )
        )
        # pylint: disable=missing-class-docstring
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed
