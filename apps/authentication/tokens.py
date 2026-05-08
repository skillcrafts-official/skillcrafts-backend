# tokens.py
from datetime import datetime, timedelta
import uuid

import jwt

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from django.conf import settings
from django.utils import timezone


class CustomAccessToken(AccessToken):
    """
    Кастомный Access Token с нашей структурой.
    """

    # Указываем тип токена
    token_type = 'access'

    def __init__(self, token=None, verify=True):
        """
        Инициализация кастомного токена.
        Если передаем строку токена - загружаем его.
        """
        if token is not None:
            # Если передан токен как строка
            self.token = token
            self.payload = self._decode_token(token, verify)
        else:
            # Создаем новый токен
            super().__init__()
            # Устанавливаем базовые claims
            self.payload['token_type'] = self.token_type
            self.payload['type'] = 'user'  # Наше кастомное поле
            self.payload['jti'] = str(uuid.uuid4())

    def _decode_token(self, token_str, verify=True):
        """
        Декодируем токен с учетом наших кастомных полей.
        """
        try:
            payload = jwt.decode(
                token_str,
                settings.SECRET_KEY,
                algorithms=[settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')],
                options={'verify_exp': verify}
            )
            return payload
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenError('Token has expired')
        except jwt.exceptions.InvalidTokenError as e:
            raise TokenError(f'Invalid token: {str(e)}')

    def set_exp(self, lifetime=None, from_time=None):
        """
        Устанавливаем срок действия токена.
        """
        if lifetime is None:
            lifetime = settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=5))

        if from_time is None:
            from_time = timezone.now()

        self.payload['exp'] = int((from_time + lifetime).timestamp())
        self.payload['iat'] = int(from_time.timestamp())
        return self

    @classmethod
    def for_user(cls, user):
        """
        Создаем access token для пользователя с нашей структурой.
        """
        token = cls()

        # Стандартные поля
        token['token_type'] = 'access'
        token['user_id'] = user.id

        # Наши кастомные поля
        token['type'] = 'user'
        token['email'] = user.email

        if user.is_staff:
            token['group'] = 'admin'
            token['permissions'] = ['full_access']
        else:
            token['group'] = 'user'
            token['permissions'] = ['user_access']

        # Устанавливаем срок действия
        token.set_exp()

        return token

    def __str__(self):
        """
        Кодируем токен в строку.
        """
        return jwt.encode(
            self.payload,
            settings.SECRET_KEY,
            algorithm=settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')
        )


class CustomRefreshToken(RefreshToken):
    """
    Кастомный Refresh Token с нашей структурой.
    """

    # Указываем тип токена
    token_type = 'refresh'
    # Указываем класс для access token
    access_token_class = CustomAccessToken

    def __init__(self, token=None, verify=True):
        """
        Инициализация кастомного refresh токена.
        """
        if token is not None:
            # Если передан токен как строка
            self.token = token
            self.payload = self._decode_token(token, verify)

            # Проверяем наши кастомные поля
            if 'type' not in self.payload or self.payload['type'] != 'user':
                raise TokenError('Token has wrong type')
        else:
            # Создаем новый токен
            super().__init__()
            # Устанавливаем базовые claims
            self.payload['token_type'] = self.token_type
            self.payload['type'] = 'user'  # Наше кастомное поле
            self.payload['jti'] = str(uuid.uuid4())

    def _decode_token(self, token_str, verify=True):
        """
        Декодируем токен с учетом наших кастомных полей.
        """
        try:
            payload = jwt.decode(
                token_str,
                settings.SECRET_KEY,
                algorithms=[settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')],
                options={'verify_exp': verify}
            )
            return payload
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenError('Token has expired')
        except jwt.exceptions.InvalidTokenError as e:
            raise TokenError(f'Invalid token: {str(e)}')

    def set_exp(self, lifetime=None, from_time=None):
        """
        Устанавливаем срок действия токена.
        """
        if lifetime is None:
            lifetime = settings.SIMPLE_JWT.get(
                'REFRESH_TOKEN_LIFETIME', timedelta(days=7)
            )

        if from_time is None:
            from_time = datetime.utcnow()

        self.payload['exp'] = int((from_time + lifetime).timestamp())
        self.payload['iat'] = int(from_time.timestamp())
        return self

    @classmethod
    def for_user(cls, user):
        """
        Создаем refresh token для пользователя с нашей структурой.
        """
        token = cls()

        # Стандартные поля
        token['token_type'] = 'refresh'
        token['user_id'] = user.id

        # Наши кастомные поля
        token['type'] = 'user'
        token['email'] = user.email

        if user.is_staff:
            token['group'] = 'admin'
            token['permissions'] = ['full_access']
        else:
            token['group'] = 'user'
            token['permissions'] = ['user_access']

        # Устанавливаем срок действия
        token.set_exp()

        return token

    @property
    def access_token(self):
        """
        Генерируем access token на основе refresh token.
        Сохраняем все наши кастомные поля.
        """
        # Создаем новый access token
        access = self.access_token_class()

        # Копируем все наши кастомные поля из refresh в access
        for key in ['user_id', 'email', 'type', 'group', 'permissions']:
            if key in self.payload:
                access[key] = self.payload[key]

        # Устанавливаем тип токена
        access['token_type'] = 'access'

        # Устанавливаем срок действия
        access.set_exp()

        return access

    def __str__(self):
        """
        Кодируем токен в строку.
        """
        return jwt.encode(
            self.payload,
            settings.SECRET_KEY,
            algorithm=settings.SIMPLE_JWT.get('ALGORITHM', 'HS256')
        )
