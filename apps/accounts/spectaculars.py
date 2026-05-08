"""Расширение автоматически сгенерированной документации"""
# pylint: disable=no-member,inherit-non-class,unnecessary-pass

from django.forms import IntegerField
from rest_framework.exceptions import status  # type: ignore
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from drf_spectacular.utils import (
    inline_serializer, extend_schema, extend_schema_view,
    OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.extensions import OpenApiViewExtension

from apps.accounts.serializers import (
    EmailConfirmSerializer, UserSerializer
)

from apps.CONSTANTS import BAD_REQUEST, NOT_AUTHENTICATED, PERMISSION_DENIED
from docs.utils import read_md_section
from docs.utils import read_md_section


# class FixUpdateUserEmailView(OpenApiViewExtension):
#     """
#     Фиксируется документация для UpdateUserEmailView
#     """
#     target_class = 'apps.accounts.views.UpdateUserEmailView'

#     def view_replacement(self) -> type[APIView]:
#         @extend_schema_view(
#             post=extend_schema(
#                 summary="Добавить новый email",
#                 description=(
#                     "Добавление нового email адреса для авторизованного "
#                     "пользователя.  \n  \n"
#                     "**Требуется аутентификация:** Да  \n"
#                     "**Права:** Только для владельца аккаунта"
#                 ),
#                 responses={
#                     status.HTTP_201_CREATED: inline_serializer(
#                         name='EmailCreated',
#                         fields={
#                             'message': serializers.CharField(),
#                         }
#                     ),
#                     status.HTTP_400_BAD_REQUEST: inline_serializer(
#                         name='EmailBadRequest',
#                         fields={
#                             'message': serializers.CharField(),
#                         }
#                     ),
#                     status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
#                     status.HTTP_403_FORBIDDEN: PERMISSION_DENIED,
#                     status.HTTP_409_CONFLICT: inline_serializer(
#                         name='EmailConflict',
#                         fields={
#                             'message': serializers.CharField()
#                         }
#                     ),
#                 },
#             )
#         )
#         # pylint: disable=missing-class-docstring
#         class Fixed(self.target_class):  # type: ignore
#             pass

#         return Fixed


class FixUpdateUserPasswordView(OpenApiViewExtension):
    """
    Фиксируется документация для UpdateUserEmailView
    """
    target_class = 'apps.accounts.views.UpdateUserPasswordView'

    def view_replacement(self) -> type[APIView]:
        @extend_schema_view(
            patch=extend_schema(
                summary="Процедура изменения пароля",
                description=read_md_section(
                    'api/accounts.md', 'PATCH /users/password/'
                ),
                responses={
                    status.HTTP_200_OK: inline_serializer(
                        name='PasswordUpdated',
                        fields={
                            'message': serializers.CharField(),
                            'success': serializers.BooleanField(),
                        }
                    ),
                    status.HTTP_400_BAD_REQUEST: BAD_REQUEST,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED,
                    status.HTTP_403_FORBIDDEN: PERMISSION_DENIED,
                    status.HTTP_409_CONFLICT: inline_serializer(
                        name='PasswordConflict',
                        fields={
                            'message': serializers.CharField()
                        }
                    ),
                },
            )
        )
        # pylint: disable=missing-class-docstring
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixUserView(OpenApiViewExtension):
    """
    Фиксируется документация для UserView
    """
    target_class = 'apps.accounts.views.UserView'

    def view_replacement(self) -> type[ModelViewSet]:

        @extend_schema_view(
            list=extend_schema(
                summary="Получение списка пользователей",
                description=read_md_section('api/accounts.md', 'GET /users/'),
                responses={
                    status.HTTP_200_OK: UserSerializer,
                    status.HTTP_401_UNAUTHORIZED: NOT_AUTHENTICATED
                }
            ),
            retrieve=extend_schema(
                summary="Получение данных пользователя",
                description=read_md_section('api/accounts.md', 'GET /users/{id}/'),
                parameters=[
                    OpenApiParameter(
                       name="id",
                       description="ID пользователя",
                       required=True,
                       type=OpenApiTypes.INT,
                       location=OpenApiParameter.PATH,
                    ),
                ],
            ),
            create=extend_schema(
                summary="Процедура регистрации пользователя",
                description=read_md_section('api/accounts.md', 'POST /users/')
            )
        )
        # pylint: disable=missing-class-docstring
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed


class FixEmailConfirmView(OpenApiViewExtension):
    """
    Фиксируется документация для EmailConfirmView
    """
    target_class = 'apps.accounts.views.EmailConfirmView'

    def view_replacement(self) -> type[APIView]:

        @extend_schema_view(
            get=extend_schema(
                summary="Получение кода подтверждения email",
                description=read_md_section(
                    'api/accounts.md', 'GET /users/email/confirm'
                ),
                parameters=[
                    OpenApiParameter(
                        name='email',
                        type=str,
                        location=OpenApiParameter.QUERY,  # ← как параметр URL
                        required=True
                    )
                ],
                responses={
                    status.HTTP_200_OK: inline_serializer(
                        name='email_code_response',
                        fields={
                            'message': serializers.CharField(
                                default='Код подтверждения email отправлен на почту!'
                            )
                        }
                    ),
                    status.HTTP_400_BAD_REQUEST: BAD_REQUEST,
                }
            ),
            post=extend_schema(
                summary="Процедура подтверждения email",
                description=read_md_section(
                    'api/accounts.md', 'POST /users/email/confirm'
                ),
                request=EmailConfirmSerializer,
                responses={
                    status.HTTP_200_OK: inline_serializer(
                        name='email_confirmation',
                        fields={
                            'verification': serializers.CharField(
                                default='passed/failed'
                            )
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
