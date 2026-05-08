# views.py - ИСПОЛЬЗУЙТЕ ЭТОТ VIEW ВМЕСТО DRF
import os
from django.http import (
    FileResponse, HttpResponseForbidden, HttpResponseNotFound
)
from django.views.decorators.http import require_GET


@require_GET
def serve_protected_media(request, path):
    """
    Отдает файлы с проверкой JWT токена
    Без DRF декораторов - не будет 406 ошибки
    """
    # 1. Проверяем JWT токен
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')

    if not auth_header.startswith('Bearer '):
        return HttpResponseForbidden('Token required')

    token = auth_header[7:]  # Убираем 'Bearer '

    # 2. Валидируем JWT (используем те же настройки что и в DRF)
    try:
        # Используем те же настройки что и в rest_framework_simplejwt
        from apps.authentication.tokens import CustomAccessToken
        access_token = CustomAccessToken(token)
        user_group = access_token['group']

        if user_group not in ('user', 'guest'):
            return HttpResponseForbidden('Invalid user group or user type')

        # Можно дополнительно проверить пользователя
        # from django.contrib.auth import get_user_model
        # User = get_user_model()
        # user = User.objects.get(id=user_id)
        # request.user = user  # Устанавливаем пользователя

    except Exception as e:
        print(f"JWT validation error: {e}")
        return HttpResponseForbidden('Invalid token')

    # 3. Отдаем файл
    file_path = os.path.join('/app/media', path)

    if not os.path.exists(file_path):
        return HttpResponseNotFound('File not found')

    # Определяем content-type
    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'

    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'

    return response
