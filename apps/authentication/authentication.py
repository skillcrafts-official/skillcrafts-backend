"""Кастомный класс для JWT аутентификации"""
import uuid
from datetime import datetime

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from apps.accounts.models import GuestUser, User

from .tokens import CustomAccessToken


class UnifiedJWTAuthentication(JWTAuthentication):
    """
    Универсальная JWT аутентификация с поддержкой кастомных токенов.
    """

    def get_validated_token(self, raw_token):
        """
        Валидируем токен, используя наш CustomAccessToken.
        Это ключевой метод, который нужно переопределить.
        """
        try:
            print("=== VALIDATING CUSTOM TOKEN ===")

            # Используем наш кастомный токен вместо стандартного
            token = CustomAccessToken(raw_token)

            # Проверяем, что это access токен
            token_type = token.payload.get('token_type')
            print(f"Token type: {token_type}")

            if token_type != 'access':
                raise InvalidToken('Token is not an access token')

            # Проверяем наше кастомное поле 'type'
            token_user_type = token.payload.get('type')
            print(f"Token user type: {token_user_type}")

            if token_user_type != 'user':
                raise InvalidToken('Token has wrong type')

            print(f"Token validated successfully")
            print(f"Token payload keys: {list(token.payload.keys())}")

            return token

        except Exception as e:
            print(f"Token validation error: {e}")
            raise InvalidToken(str(e))

    def get_user(self, validated_token):
        """
        Получение пользователя на основе кастомного токена.
        """
        print("=== GET_USER CALLED WITH CUSTOM TOKEN ===")

        # Определяем тип пользователя из токена
        # В нашем кастомном токене это поле 'group'
        user_type = validated_token.get('group', 'user')
        print(f"User type from token: {user_type}")

        if user_type == 'guest':
            # Гостевой пользователь
            guest_id = validated_token.get('guest_id')
            print(f"Guest ID: {guest_id}")

            if not guest_id:
                return None

            try:
                # Преобразуем строку в UUID
                guest_uuid = uuid.UUID(str(guest_id))
            except (ValueError, AttributeError):
                print(f"Invalid UUID format: {guest_id}")
                return None

            try:
                guest = GuestUser.objects.get(guest_uuid=guest_uuid)
                guest.last_activity = datetime.now()
                guest.save(update_fields=['last_activity'])
                print(f"Guest found: {guest}")
                return guest
            except GuestUser.DoesNotExist:
                print(f"Guest not found, creating new: {guest_id}")
                # Создаем нового гостя
                return GuestUser.objects.create(
                    guest_id=guest_uuid,
                    last_activity=datetime.now()
                )

        else:
            # Обычный пользователь (user или admin)
            user_id = validated_token.get('user_id')
            print(f"User ID from token: {user_id}")

            if not user_id:
                return None

            try:
                # Пробуем как UUID
                user_uuid = uuid.UUID(str(user_id))
                user = User.objects.get(id=user_uuid)
                print(f"User found by UUID: {user}")
                print(f"User email: {user.email}")
                print(f"User is staff: {user.is_staff}")
                return user
            except (ValueError, AttributeError):
                # Если не UUID, пробуем как число (для обратной совместимости)
                try:
                    user = User.objects.get(pk=user_id)
                    print(f"User found by numeric ID: {user}")
                    return user
                except (ValueError, User.DoesNotExist):
                    print(f"User not found: {user_id}")
                    return None
            except User.DoesNotExist:
                print(f"User not found: {user_id}")
                return None
