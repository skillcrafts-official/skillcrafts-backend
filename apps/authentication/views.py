from typing import Any
from django.db.models.query import QuerySet
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError

from rest_framework.request import Request
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)

from apps.accounts.models import User
from apps.authentication.serializers import (
    MyTokenObtainPairSerializer,
    # GuestTokenObtainSerializer,
    MyTokenRefreshSerializer,
    MyTokenVerifySerializer
)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Кастомное представление для получения токенов.
    """
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def check_permissions(self, request: Request) -> None:
        email = request.data.get('email', None)
        if email is None:
            raise ValidationError(detail={
                'error': 'Email field is required'
            })

        user = User.objects.filter(email=email, email_verified=True).first()

        if user is None:
            raise PermissionDenied(detail={
                'detail': 'Email не подтверждён!'
            })

        return super().check_permissions(request)


class MyTokenRefreshView(TokenRefreshView):
    """
    Кастомное представление для обновления access токена.
    """
    serializer_class = MyTokenRefreshSerializer
    permission_classes = [AllowAny]


class MyTokenVerifyView(TokenVerifyView):
    """
    Кастомное представление для верификации токенов.
    """
    serializer_class = MyTokenVerifySerializer
    permission_classes = [AllowAny]


# расширение для релиза 0.2.0.0
# class GuestTokenObtainView(APIView):
#     """Получение гостевого токена"""
#     serializer_class = GuestTokenObtainSerializer  # Используйте исправленный сериализатор
#     permission_classes = [AllowAny]
#     authentication_classes = []

#     def post(self, request, *args, **kwargs):
#         ip_address = request.META.get('REMOTE_ADDR', '')
#         user_agent = request.META.get('HTTP_USER_AGENT', '')
#         # print(f"Creating guest token for IP: {ip_address}")
#         # print(f"User-Agent: {user_agent}")

#         try:
#             serializer = self.serializer_class(
#                 data={},
#                 context={'request': request}
#             )
#             serializer.is_valid(raise_exception=True)
#             return Response(serializer.validated_data)
#         except Exception as e:
#             print(f"Error creating guest token: {str(e)}")
#             raise


# class MigrateGuestToUserView(APIView):
#     """Миграция гостя в полноценного пользователя"""

#     def post(self, request):
#         guest = request.user  # Гость из GuestAuthentication

#         # Валидация данных регистрации
#         email = request.data.get('email')
#         password = request.data.get('password')

#         # Создаём пользователя
#         user = User.objects.create(
#             primary_email=email,
#             password=password,
#             guest_origin=guest
#         )

#         # Мигрируем данные гостя
#         # if guest.cart_items:
#         #     # Переносим корзину
#         #     for item in guest.cart_items:
#         #         CartItem.objects.create(
#         #             user=user,
#         #             product_id=item['product_id'],
#         #             quantity=item['quantity']
#         #         )

#         # if guest.preferences:
#         #     # Переносим настройки
#         #     user.profile.preferences.update(guest.preferences)
#         #     user.profile.save()

#         # Генерируем обычный JWT для пользователя
#         from rest_framework_simplejwt.tokens import RefreshToken
#         refresh = RefreshToken.for_user(user)

#         # Помечаем гостя как мигрированного
#         guest.migrated_to = user
#         guest.save()

#         return Response({
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#             'user_id': user.pk,
#             'guest_data_migrated': True
#         })


# class GuestConsentView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         """Регистрация согласия гостя"""
#         guest_id = request.data.get('guest_id')
#         consent_type = request.data.get('consent_type', 'basic')

#         # Получаем текст политики (актуальную версию)
#         policy_text = get_current_policy_text()
#         policy_hash = hash_text(policy_text)

#         # Сохраняем согласие
#         consent = GuestConsent.objects.create(
#             guest_id=guest_id,
#             consent_type=consent_type,
#             ip_address=get_client_ip(request),
#             user_agent=request.META.get('HTTP_USER_AGENT', ''),
#             consent_text_hash=policy_hash
#         )

#         return Response({
#             'status': 'consent_registered',
#             'consent_id': consent.pk,
#             'policy_version': policy_hash[:8]
#         })


# class GuestConsentWithdrawView(APIView):
#     def post(self, request):
#         """Отзыв согласия (право быть забытым)"""
#         guest = request.user

#         # Помечаем согласие как отозванное
#         GuestConsent.objects.filter(
#             guest=guest,
#             is_active=True
#         ).update(
#             is_active=False,
#             withdrawn_at=timezone.now()
#         )

#         # Анонимизируем данные гостя
#         guest.user_agent = ''
#         guest.ip_address = None
#         guest.save()

#         return Response({'status': 'consent_withdrawn'})
