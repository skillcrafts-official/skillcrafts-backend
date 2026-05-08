import hashlib

from django.db import models

from rest_framework import serializers

from apps.accounts.models import User, GuestUser

from docs.utils import read_md_section


class BaseConsent:
    def get_current_consent_policy(self):
        """Возвращает актуальный текст соглашения"""
        return read_md_section('consents/policy.md')

    def get_current_personal_consent(self):
        """Возвращает актуальный текст соглашения"""
        return read_md_section('consents/personal_data.md')

    def generate_text_hash(self, text):
        """Генерирует хэш текста соглашения"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def check_consent(self, ConsentInstance: models.Model, **kwargs):
        active_consent = ConsentInstance.objects.filter(
            is_active=True,
            **kwargs
        ).first()

        if not active_consent:
            # Если согласия нет - создаём новое
            consent_policy = self.get_current_consent_policy()
            consent_policy_hash = self.generate_text_hash(consent_policy)
            personal_consent = self.get_current_personal_consent()
            personal_consent_hash = self.generate_text_hash(personal_consent)

            user_params = {
                **kwargs
            }

            if kwargs.get('guest', None):
                user_params.update({
                    'ip_address': kwargs['guest'].ip_address,
                    'user_agent': kwargs['guest'].user_agent
                })

            consent = ConsentInstance.objects.create(
                consent_policy=consent_policy_hash,
                personal_consent=personal_consent_hash,
                **user_params
                # is_active=True по умолчанию
                # withdrawn_at=None по умолчанию
            )

        # Проверяем, не было ли согласие отозвано
        if ConsentInstance.objects.filter(
            is_active=False, **kwargs
        ).exists():
            raise serializers.ValidationError({
                'detail': 'Согласие на обработку данных было отозвано',
                'code': 'consent_withdrawn'
            })


class GuestConsent(models.Model):
    guest = models.ForeignKey(GuestUser, on_delete=models.CASCADE)
    consent_type = models.CharField(max_length=50)  # 'basic', 'cookies', 'marketing'
    given_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    consent_text_hash = models.CharField(max_length=64)  # Хэш текста политики на момент согласия

    # Для GDPR/РКН compliance
    is_active = models.BooleanField(default=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)


class UserConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # consent_type = models.CharField(max_length=50)  # 'policy', 'personal data'
    given_at = models.DateTimeField(auto_now=True)
    # ip_address = models.GenericIPAddressField()
    # user_agent = models.TextField()

    # Хэш текста политики на момент согласия
    consent_policy = models.CharField(max_length=64)
    # Хэш текста согласия на обработку персональных данных
    personal_consent = models.CharField(max_length=64)

    # Для GDPR/РКН compliance
    is_active = models.BooleanField(default=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
