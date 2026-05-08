import re
from typing import Any
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.utils import timezone

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.consents.models import BaseConsent, UserConsent


class ValidationFields:
    def validate_password(self, value: str) -> str:
        """
        Реализует валидацию пароля по общим правил с фронтендом
        1. Количество символов - не менее 8
        2. Английские буквы в нижнем ([a-z]) и верхнем регистрах ([A-Z])
        3. Спецсимволы ([!@#$%^&*()_+-=[]{};':"|,.<>/?])
        Пример правильного пароля asdfASDF1!
        """
        special_chars = re.escape("""!@#$%^&*()_+-=[]{};':"|,.<>/?""")
        requirements = {
            'has_min_chars': lambda pwd: len(pwd) >= 8,
            'has_digit': lambda pwd: bool(re.search(r'\d', pwd)),
            'has_lowercase': lambda pwd: bool(re.search(r'[a-z]', pwd)),
            'has_uppercase': lambda pwd: bool(re.search(r'[A-Z]', pwd)),
            'has_special_chars': lambda pwd: bool(
                re.search(rf'[{special_chars}]', pwd)
            ),
        }
        for req, check in requirements.items():
            if not check(value):
                raise serializers.ValidationError(f'Нарушено условие: {req}')
        return value

    def validate_consent_policy(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError(
                'Для пользования сервисом необходимо '
                'принять политику конфиденциальности'
            )
        return value

    def validate_personal_consent(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError(
                'Для пользования сервисом необходимо '
                'дать согласие на обработку персональных данных'
            )
        return value


class UserSerializer(BaseConsent, ValidationFields, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    consent_policy = serializers.BooleanField(write_only=True)
    personal_consent = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            'pk', 'email',
            'password', 'consent_policy', 'personal_consent'
        ]

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        validated_data.pop('consent_policy')
        validated_data.pop('personal_consent')
        user = User.objects.create(**validated_data)
        self.check_consent(UserConsent, user=user)
        return user


class EmailConfirmSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'confirmation_code']

    def validate(self, attrs: Any) -> Any:
        confirmed_email = attrs.pop('email', None)
        confirm_code = attrs.pop('confirmation_code', None)

        try:
            if not all((
                self.instance.email == confirmed_email,
                self.instance.confirmation_code == confirm_code,
                (timezone.now() - self.instance.generated_code_at) <= timedelta(minutes=15)
            )):
                raise ValidationError(detail={
                    'message': 'Время действия кода подтверждения истекло!'
                })
        except Exception as e:
            print(str(e))

        if self.instance.email_verified:
            raise ValidationError(detail={
                'message': 'Email уже подтверждён!'
            })

        self.instance.email_verified = True
        self.instance.save()

        return super().validate(attrs)

    def create(self, validated_data):
        pass


class UserPasswordSerializer(ValidationFields, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['password']
