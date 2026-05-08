"""Serializers for auth"""

# from typing import Any

from django.contrib.auth import authenticate

from rest_framework import serializers

from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer, TokenRefreshSerializer, TokenVerifySerializer
)

from apps.consents.models import BaseConsent, UserConsent
from apps.accounts.models import User

from .tokens import CustomAccessToken, CustomRefreshToken


class MyTokenObtainPairSerializer(BaseConsent, TokenObtainPairSerializer):
    """
    Кастомный сериализатор для получения токенов.
    Использует наши кастомные токены.
    """

    def validate(self, attrs):
        # Аутентификация пользователя
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }

        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not self.user:
            raise serializers.ValidationError(
                'Неверные учетные данные',
                code='authorization'
            )

        if not self.user.is_active:
            raise serializers.ValidationError(
                'Пользователь неактивен',
                code='authorization'
            )

        # Проверяем согласие (ваш существующий код)
        try:
            self.check_consent(UserConsent, user=self.user)
        except Exception as e:
            raise serializers.ValidationError(str(e))

        # Создаем кастомные токены
        refresh = CustomRefreshToken.for_user(self.user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': self.user.pk,
            'email': self.user.email,
            'group': 'admin' if self.user.is_staff else 'user',
        }

        return data

    @classmethod
    def get_token(cls, user):
        """
        Переопределяем для совместимости с родительским классом.
        """
        return CustomRefreshToken.for_user(user)


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Кастомный сериализатор для обновления access токена.
    Работает с нашими кастомными токенами.
    """

    def validate(self, attrs):
        refresh_token = attrs.get('refresh')

        if not refresh_token:
            raise InvalidToken('Refresh token is required')

        try:
            # Создаем кастомный refresh токен из строки
            refresh = CustomRefreshToken(refresh_token)

            # Проверяем, что токен правильного типа
            if refresh.payload.get('type') != 'user':
                raise InvalidToken('Token has wrong type')

            # Проверяем, что это refresh токен
            if refresh.payload.get('token_type') != 'refresh':
                raise InvalidToken('Token is not a refresh token')

            # Получаем пользователя из токена
            user_id = refresh.payload.get('user_id')
            if not user_id:
                raise InvalidToken('Token has no user_id claim')

            # Получаем пользователя
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise InvalidToken('User not found')

            # Проверяем активность пользователя
            if not user.is_active:
                raise InvalidToken('User is not active')

            access_token = refresh.access_token

            return {
                'access': str(access_token),
                'refresh': str(refresh),  # Тот же refresh токен
            }

        except Exception as e:
            raise InvalidToken(str(e))


class MyTokenVerifySerializer(TokenVerifySerializer):
    """
    Кастомный сериализатор для верификации токенов.
    Работает с нашими кастомными токенами.
    """

    def validate(self, attrs):
        token = attrs.get('token')

        if not token:
            raise InvalidToken('Token is required')

        try:
            # Пробуем декодировать как access токен
            access = CustomAccessToken(token)

            # Проверяем тип
            if access.payload.get('type') != 'user':
                raise InvalidToken('Token has wrong type')

            if access.payload.get('token_type') != 'access':
                raise InvalidToken('Token is not an access token')

            # Если нужно, можно проверить пользователя
            user_id = access.payload.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    if not user.is_active:
                        raise InvalidToken('User is not active')
                except User.DoesNotExist:
                    pass  # Игнорируем, если пользователь не найден

            return {}

        except Exception as e:
            # Если не access, пробуем как refresh
            try:
                refresh = CustomRefreshToken(token)

                if refresh.payload.get('type') != 'user':
                    raise InvalidToken('Token has wrong type')

                if refresh.payload.get('token_type') != 'refresh':
                    raise InvalidToken('Token is not a refresh token')

                return {}

            except Exception:
                # Если оба варианта не сработали
                raise InvalidToken(str(e))


# Расширение для релиза 0.2.0.0
# class GuestTokenObtainSerializer(BaseConsent, serializers.Serializer):
#     """
#     Сериализатор для получения гостевого токена
#     """

#     def validate(self, attrs):
#         """
#         Главный метод валидации, который вызывается при serializer.is_valid()
#         """
#         return self.create_guest_token()

#     def create_guest_token(self):
#         """Генерация гостевого токена"""
#         request = self.context.get('request')

#         if not request:
#             raise serializers.ValidationError({
#                 'detail': 'Request context is required for guest token',
#                 'code': 'no_request_context'
#             })

#         # Генерируем уникальный guest_id
#         guest_id = str(uuid.uuid4())

#         # Создаём или находим гостя
#         guest, created = GuestUser.objects.get_or_create(
#             guest_uuid=guest_id,
#             defaults={
#                 'user_agent': request.META.get('HTTP_USER_AGENT', ''),
#                 'ip_address': request.META.get('REMOTE_ADDR', ''),
#             }
#         )

#         # Обновляем активность
#         guest.save()

#         self.check_consent(GuestConsent, guest=guest)
#         # active_consent = GuestConsent.objects.filter(
#         #     guest=guest,
#         #     is_active=True,
#         #     consent_type='registration'
#         # ).first()

#         # if not active_consent:
#         #     # Если согласия нет - создаём новое
#         #     consent_text = self.get_current_consent_text()
#         #     consent_hash = self.generate_text_hash(consent_text)

#         #     guest_consent = GuestConsent.objects.create(
#         #         guest=guest,
#         #         consent_type='registration',
#         #         ip_address=guest.ip_address,
#         #         user_agent=guest.user_agent,
#         #         consent_text_hash=consent_hash,
#         #         # is_active=True по умолчанию
#         #         # withdrawn_at=None по умолчанию
#         #     )

#         # # Проверяем, не было ли согласие отозвано
#         # if GuestConsent.objects.filter(
#         #     guest=guest, is_active=False, consent_type='registration'
#         # ).exists():
#         #     raise serializers.ValidationError({
#         #         'detail': 'Согласие на обработку данных было отозвано',
#         #         'code': 'consent_withdrawn'
#         #     })

#         # Генерируем JWT токен для гостя
#         from rest_framework_simplejwt.tokens import RefreshToken

#         refresh = RefreshToken()
#         refresh['type'] = 'guest'
#         refresh['guest_id'] = str(guest.guest_uuid)
#         refresh['group'] = 'guest'
#         refresh['permissions'] = ['guest_access']
#         refresh['user_id'] = str(guest.guest_uuid)

#         # В access токен (ОБЯЗАТЕЛЬНО!)
#         refresh.access_token['type'] = 'guest'  # ← И ЭТО ТОЖЕ ВАЖНО!
#         refresh.access_token['guest_id'] = str(guest.guest_uuid)
#         refresh.access_token['user_id'] = str(guest.guest_uuid)

#         # Устанавливаем время жизни
#         from datetime import timedelta
#         from django.conf import settings

#         guest_lifetime = settings.SIMPLE_JWT.get('GUEST_TOKEN_LIFETIME', timedelta(days=30))
#         refresh.access_token.set_exp(lifetime=guest_lifetime)

#         return {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#             'user_type': 'guest',
#             'guest_id': str(guest.guest_uuid),
#             'user_id': str(guest.guest_uuid),  # Для совместимости
#         }
