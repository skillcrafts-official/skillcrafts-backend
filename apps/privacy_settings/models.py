"""
Модели для тонкой настройки доступа к информации системы
"""
from django.db import models

from rest_framework.exceptions import NotFound

from apps.profiles.models import Profile
from apps.accounts.models import User

from apps.CONSTANTS import PRIVACIES


class ProfilePrivacySettings(models.Model):
    """
    Модель для настройки доступа к информации о пользователе
    """
    first_name = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    middle_name = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    last_name = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    profession = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    city = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    country = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    relocation = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    work_formats = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    edu_level = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    institution_name = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    graduation_year = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    short_desc = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    full_desc = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    wallpaper = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    avatar = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    link_to_instagram = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    link_to_telegram = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    link_to_github = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )
    link_to_vk = models.CharField(
        choices=PRIVACIES, max_length=20, default='all'
    )

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile_privacies'
    )
    blacklist = models.ManyToManyField(
        User, related_name='profile_blacklist', blank=True
    )
    whitelist = models.ManyToManyField(
        User, related_name='profile_whitelist', blank=True
    )

    class Meta:
        verbose_name = 'Доступ к профилю пользователя'
        verbose_name_plural = 'Доступ к профилям пользователей'

    def __iter__(self):
        for field in self._meta.fields:  # pylint: disable=no-member
            if not field.auto_created:
                yield field.name, getattr(self, field.name)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    # @classmethod
    # def get_profile(cls, user_id):
    #     """Получаем профиль по user_id"""
    #     try:
    #         profile = cls.objects.get(user_id=user_id)
    #     except cls.DoesNotExist:
    #         profile = None

    #     if profile is None:
    #         raise NotFound(
    #             detail="Profile not found"
    #         )

    #     return profile


class TaskPrivacySettings(models.Model):
    """
    Модель для настройки доступа к информации о задачах пользователя
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='task_privacies'
    )
    blacklist = models.ManyToManyField(
        User, related_name='task_blacklist', blank=True
    )
    whitelist = models.ManyToManyField(
        User, related_name='task_whitelist', blank=True
    )

    class Meta:
        verbose_name = 'Доступ к задаче пользователя'
        verbose_name_plural = 'Доступ к задачам пользователей'

    def __iter__(self):
        for field in self._meta.fields:  # pylint: disable=no-member
            if not field.auto_created:
                yield field.name, getattr(self, field.name)

    # @classmethod
    # def get_profile(cls, user_id):
    #     """Получаем профиль по user_id"""
    #     try:
    #         profile = cls.objects.get(user_id=user_id)
    #     except cls.DoesNotExist:
    #         profile = None

    #     if profile is None:
    #         raise NotFound(
    #             detail="Profile not found"
    #         )

    #     return profile
