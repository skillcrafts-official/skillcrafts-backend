import uuid

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


class GuestUser(models.Model):
    """Анонимный гость для хранения временных данных"""
    guest_uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    user_agent = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Связь с будущим пользователем
    migrated_to = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        verbose_name = "Гостевой пользователь"
        verbose_name_plural = "Гостевые пользователи"
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Guest {self.guest_uuid}"

    @property
    def is_authenticated(self):
        """Всегда возвращает True для аутентификации в DRF"""
        return True

    @property
    def is_anonymous(self):
        """Всегда возвращает False"""
        return False

    def get_username(self):
        """Возвращает username-подобное значение"""
        return f"guest_{self.guest_uuid}"


class User(AbstractUser):
    user_uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )
    username = None
    confirmation_code = models.CharField(
        max_length=4, default='0000', blank=True
    )
    email = models.EmailField(unique=True, blank=False)

    generated_code_at = models.DateTimeField(null=True, blank=True)

    email_verified = models.BooleanField(default=False)

    guest_origin = models.ForeignKey(
        GuestUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='migrated_user'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def set_active_email(self, email_instance):
        """Установить активный email"""
        if email_instance.user != self:
            raise ValueError("Email does not belong to this user")
        email_instance.is_active = True
        email_instance.save()

    def __iter__(self):
        # для итерации по полям модели User
        for field in self._meta.fields:
            if not field.auto_created:
                yield field.name, getattr(self, field.name)

    def __str__(self):
        return str(self.email)
