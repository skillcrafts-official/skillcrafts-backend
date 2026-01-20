"""The DRF documentation extends for app consents"""
# pylint: disable=no-member,inherit-non-class,unnecessary-pass
from rest_framework import serializers, status
from rest_framework.viewsets import ModelViewSet

from drf_spectacular.utils import (
    inline_serializer, extend_schema, extend_schema_view,
)

from drf_spectacular.extensions import (
    OpenApiViewExtension, OpenApiAuthenticationExtension
)

from apps.CONSTANTS import BAD_REQUEST, NOT_AUTHENTICATED
from docs.utils import read_md_section


class FixUserConsentViewSet(OpenApiViewExtension):
    """
    Фиксирует расширение документации для UserConsentViewSet
    """
    target_class = 'apps.consents.views.UserConsentViewSet'

    def view_replacement(self) -> type[ModelViewSet]:

        @extend_schema_view(
            get_policy=extend_schema(
                summary="Политика конфиденциальности",
                description=read_md_section('consents/policy.md'),
                responses={
                    status.HTTP_200_OK: inline_serializer(
                        name='policy_response',
                        fields={
                            'policy': serializers.CharField(
                                default='current policy...'
                            )
                        }
                    ),
                }
            ),
            get_personal=extend_schema(
                summary="Согласие на обработку персональных данных",
                description=read_md_section('consents/personal_data.md'),
                responses={
                    status.HTTP_200_OK: inline_serializer(
                        name='personal_data_processing_response',
                        fields={
                            'personal_data_process': serializers.CharField(
                                default='current personal data processing...'
                            )
                        }
                    ),
                }
            )
        )
        # pylint: disable=missing-class-docstring
        class Fixed(self.target_class):  # type: ignore
            pass

        return Fixed
