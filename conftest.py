"""
Global conftest.py
Общие для всех уровней тестов фабрики фикстур
"""

import tempfile
import shutil
import pytest

from django.test import override_settings

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# собираем все conftest воедино
pytest_plugins = [
    'apps.accounts.tests.conftest',
    'apps.profiles.tests.conftest',
]


@pytest.fixture
def temp_media():
    """Создает временную MEDIA_ROOT которая автоматически удаляется"""
    temp_dir = tempfile.mkdtemp()

    with override_settings(MEDIA_ROOT=temp_dir):
        yield temp_dir

    # Удаляем временную папку после теста
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def auth_client():
    """Фабрика API клиентов с JWT токеном в заголовках"""
    def create_auth_client(user=None):
        client = APIClient()
        if user is not None:
            refresh = RefreshToken.for_user(user)  # type: ignore
            client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}'
            )
        return client
    return create_auth_client
