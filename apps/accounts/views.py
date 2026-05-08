from collections.abc import Sequence
from typing import Any
from datetime import datetime

from jsonschema import ValidationError
from apps.authentication.authentication import UnifiedJWTAuthentication
from django.db import IntegrityError
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.core.email_utils import send_confirmation_email

from .models import User
from .serializers import (
    UserSerializer, UserPasswordSerializer,
    EmailConfirmSerializer
)
from .permissions import IsAdminOrModerator


class UserView(ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrModerator]
    lookup_field = 'pk'

    def get_permissions(self) -> Sequence:
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()


class EmailConfirmView(APIView):
    """Ендпоинты для подтверждения Email"""
    serializer_class = EmailConfirmSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email', '')
        print(email)
        user = User.objects.filter(email=email, email_verified=False).first()

        if user is None:
            raise ValidationError(detail={
                'error': 'User not found or email is verified!'
            })

        result = send_confirmation_email(
            email=user.email,
            username=user.email
        )
        user.confirmation_code = result['code'] or 'TEST'
        user.generated_code_at = timezone.now()
        user.save(update_fields=['confirmation_code', 'generated_code_at'])

        return Response({
            'message': 'Код подтверждения email отправлен на почту!'
        })

    def post(self, request, *args, **kwargs):
        """Проверка email"""
        data = request.data

        user = User.objects.filter(
            email=data.get('email', ''),
            confirmation_code=data.get('confirmation_code', '')
        ).first()

        if user is None:
            raise ValidationError(detail='User not found!')

        serializer = self.serializer_class(
            instance=user, data=data, partial=True
        )

        if serializer.is_valid():
            return Response({'verification': 'passed'}, status=200)

        return Response({'errors': serializer.error_messages}, status=400)


class UpdateUserPasswordView(APIView):
    serializer_class = UserPasswordSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            user = request.user
            user.password = make_password(
                serializer.validated_data['password']
            )
            user.save()
            return Response(
                data={
                    "message": "Password has been successfully updated!",
                    "success": True
                }, status=status.HTTP_200_OK
            )
        return Response(
            data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
