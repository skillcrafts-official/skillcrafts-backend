"""Local conftest.py"""
# pylint: disable=no-member

import pytest

from apps.accounts.models import User


@pytest.fixture
def users_pool():
    """Пул пользователей"""
    # pylint: disable=too-few-public-methods
    class UsersPool:
        """
        Создаёт именные атрибуты пользователей
        """
        def __init__(self, quantity: int = 1):
            for i in range(quantity):
                user_data = {
                    'primary_email': f'testuser{i + 1}@example.com',
                    'password': 'testpass123'
                }
                setattr(
                    self, f'user{i + 1}',
                    User.objects.create(**user_data)
                )

        def __iter__(self):
            # для итерации по моделям User
            yield from self.__dict__.values()

    return UsersPool


@pytest.fixture
def emails_pool():
    """Фабрика пулов имейлов для пользователя"""
    # pylint: disable=too-few-public-methods
    def create_pool(user: User, quantity: int = 1):
        class EmailsPool:
            """
            Создаёт именные атрибуты emails
            """
            def __init__(self, quantity):
                for i in range(quantity):
                    email_data = {
                        'email': f'testuser{i + 1}@example.com',
                        'user': user
                    }
                    setattr(
                        self, f'email{i + 1}',
                        Email.objects.create(**email_data)
                    )

            def __iter__(self):
                # для итерации по моделям User
                yield from self.__dict__.values()

        return EmailsPool(quantity)
    return create_pool
