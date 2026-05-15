"""Тесты для представлений (View)"""
# pylint: disable=no-member
from urllib.parse import urlparse
import pytest

from django.urls import NoReverseMatch, reverse

from rest_framework import status

from apps.utils import create_test_image


@pytest.mark.django_db
class TestUserProfileView:
    """
    Проверяется выдача информации по запросу
    авторизованного пользователя о другом пользователе
    """
    def test_get_user_profile_by_user_id(
            self, auth_client, users_profiles, temp_media
    ):
        """
        Тест выдачи профиля пользователя
        в контексте авторизованного пользователя
        """
        users, profiles = users_profiles(2)
        # profiles = map(lambda x: x[0], profiles)

        urls = [
            reverse('user_profile', kwargs={'pk': pk})
            for pk, _ in enumerate(users, 1)
        ]

        responses = [
            auth_client(users.user1).get(url)
            for url in urls
        ]
        # проверка статус кода (200)
        assert all((
            response.status_code == status.HTTP_200_OK
            for response in responses
        ))
        # проверка типа контента
        assert all((
            response.headers.get('Content-Type') == 'application/json'
            for response in responses
        ))
        # проверка наличия токена аутентификации в запросе
        assert all((
            response.wsgi_request.META
            .get('HTTP_AUTHORIZATION', None).startswith('Bearer ')

            for response in responses
        ))
        # проверка по типу поля (CharField)
        assert all((
            response.data.get('first_name', None) == profile.first_name
            for response, profile in zip(responses, profiles)
        ))
        # проверка по типу поля (URLField)
        assert all((
            response.data.get('link_to_github', None) == profile.link_to_github
            for response, profile in zip(responses, profiles)
        ))
        # проверка по типу поля (ImageField)
        assert all((
            urlparse(response.data.get('avatar', None)).path ==
            getattr(profile.avatar, 'url', None)

            for response, profile in zip(responses, profiles)
        ))
        # проверка по типу поля (ForeignKey)
        assert all((
            response.data.get('user', None) == profile.user.id
            for response, profile in zip(responses, profiles)
        ))

    @pytest.mark.parametrize(
        'user_id', [0, 100_000]
    )
    def test_get_user_profile_by_non_existent_user(
            self, auth_client, users_profiles, user_id, temp_media
    ):
        """
        Тест на попытку получить данные по несуществующим пользователям
        """
        users, _ = users_profiles(1)

        url = reverse('user_profile', kwargs={'pk': user_id})

        response = auth_client(users.user1).get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_4xx_status_codes(self, auth_client, users_profiles, temp_media):
        """
        Тесты ошибок статус кодов: 401
        """
        users, _ = users_profiles(1)
        url = reverse('user_profile', kwargs={'pk': users.user1.id})

        response = auth_client(
            # users.user1,  <- убирается аутентификация из запроса
        ).get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_self_user_profile(
            self, auth_client, users_profiles, profile_data, temp_media
    ):
        """
        Тест выдачи информации о самом себе
        в контексте собственной авторизации
        """
        # создаются два оригинальных пользователя с профилями
        users, profiles = users_profiles(2)

        profile1 = profile_data()  # профиль для обновления первого юзера
        profile2 = profile_data()  # профиль для обновления второго юзера

        url1 = reverse('user_profile', kwargs={'pk': users.user1.profile.pk})
        url2 = reverse('user_profile', kwargs={'pk': users.user2.profile.pk})

        # проверяем обновление профиля для первого пользователя
        response = auth_client(users.user1).post(
            url1, profile1, format='multipart'
        )
        assert response.status_code == status.HTTP_200_OK
        for field in profile1:
            assert response.data.get(field, None)

        # проверяем обновление профиля пользователя неавторизованным юзером
        response = auth_client(
            # users.user1  <- убирается аутентификация из запроса
        ).post(url1, profile2, format='multipart')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # проверяем отправку данных profile2 для чужого профиля
        response = auth_client(users.user1).post(
            url2, profile2, format='multipart'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_self_user_profile(
            self, auth_client, users_profiles, temp_media
    ):
        """
        Тест удаления профиля пользователя
        """
        users, _ = users_profiles(2)
        url1 = reverse('user_profile', kwargs={'pk': 1})
        url2 = reverse('user_profile', kwargs={'pk': 2})

        # проверяем, что анонимно удалить профиль нельзя
        response = auth_client(
            # users.user1  <- убирается аутентификация из запроса
        ).delete(url1)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # проверяем, что удалить чужой профиль нельзя
        response = auth_client(users.user1).delete(url2)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # проверяем удаление самого себя
        response = auth_client(users.user1).delete(url1)
        assert response.status_code == status.HTTP_204_NO_CONTENT
