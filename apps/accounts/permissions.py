# apps/accounts/permissions.py
from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser


class PermissionRegistry:
    """
    Реестр прав для разных типов пользователей
    """
    PERMISSIONS = {
        'guest': ['read_all', 'read_public', 'create_comment'],  # Гости
        'user': ['read_all', 'create_post', 'edit_own', 'delete_own', 'create_comment'],  # Обычные пользователи
        'admin': ['full_access'],  # Администраторы
        'moderator': ['read_all', 'create_post', 'edit_any', 'delete_any', 'moderate'],  # Модераторы
    }

    @classmethod
    def get_permissions(cls, user):
        """Возвращает список прав пользователя"""
        if hasattr(user, 'guest_id'):
            return cls.PERMISSIONS['guest']
        elif user.is_staff:
            return cls.PERMISSIONS['admin'] if user.is_superuser else cls.PERMISSIONS.get('moderator', [])
        else:
            return cls.PERMISSIONS['user']


class BasePermissionWithType(permissions.BasePermission):
    """
    Базовый класс для permissions с информацией о типе пользователя
    """
    def get_user_type(self, user):
        """Определяет тип пользователя"""
        if isinstance(user, AnonymousUser):
            return 'anonymous'
        elif hasattr(user, 'guest_id'):
            return 'guest'
        elif user.is_superuser:
            return 'admin'
        elif user.is_staff:
            return 'moderator'
        else:
            return 'user'

    def has_permission(self, request, view):
        # По умолчанию проверяем тип пользователя
        user_type = self.get_user_type(request.user)
        return user_type != 'anonymous'


class IsGuestOnly(BasePermissionWithType):
    """Только для гостей"""
    def has_permission(self, request, view):
        return self.get_user_type(request.user) == 'guest'


class IsAuthenticatedUser(BasePermissionWithType):
    """Только для аутентифицированных пользователей (не гостей)"""
    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)
        return user_type in ['user', 'moderator', 'admin']


class IsAdminOrModerator(BasePermissionWithType):
    """Только для администраторов и модераторов"""
    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)
        return user_type in ['admin', 'moderator']


class IsAdminOnly(BasePermissionWithType):
    """Только для администраторов"""
    def has_permission(self, request, view):
        return self.get_user_type(request.user) == 'admin'


class IsAccountOwner(BasePermissionWithType):
    def has_permission(self, request, view):
        return super().has_permission(request, view)


# apps/accounts/permissions.py
class ReadOnly(BasePermissionWithType):
    """
    Разрешает только безопасные методы (GET, HEAD, OPTIONS)
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False


class CanCreate(BasePermissionWithType):
    """
    Разрешает создание (POST)
    """
    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)

        if request.method == 'POST':
            if user_type == 'guest':
                # Гости могут создавать только комментарии
                return view.__class__.__name__ in ['CommentViewSet', 'CommentListCreateView']
            elif user_type == 'user':
                return True  # Обычные пользователи могут создавать
            elif user_type in ['moderator', 'admin']:
                return True  # Модераторы и админы могут создавать

        return False


class CanUpdate(BasePermissionWithType):
    """
    Разрешает обновление (PUT, PATCH)
    """
    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)

        if request.method in ['PUT', 'PATCH']:
            if user_type == 'guest':
                return False  # Гости не могут обновлять
            elif user_type == 'user':
                # Проверка владения объектом будет в has_object_permission
                return True
            elif user_type in ['moderator', 'admin']:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        """Проверка прав на конкретный объект"""
        user_type = self.get_user_type(request.user)

        if user_type == 'user':
            # Пользователь может редактировать только свои объекты
            return hasattr(obj, 'user') and obj.user == request.user
        elif user_type in ['moderator', 'admin']:
            # Модераторы и админы могут редактировать любые
            return True

        return False


class CanDelete(BasePermissionWithType):
    """
    Разрешает удаление (DELETE)
    """
    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)

        if request.method == 'DELETE':
            if user_type == 'guest':
                return False
            elif user_type == 'user':
                return True
            elif user_type in ['moderator', 'admin']:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        user_type = self.get_user_type(request.user)

        if user_type == 'user':
            return hasattr(obj, 'user') and obj.user == request.user
        elif user_type in ['moderator', 'admin']:
            return True

        return False


# apps/accounts/permissions.py
class ReadOnlyForGuests(BasePermissionWithType):
    """
    Гости - только чтение, пользователи - полный доступ
    """
    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)

        if user_type == 'guest':
            # Гости - только безопасные методы
            return request.method in permissions.SAFE_METHODS
        elif user_type in ['user', 'moderator', 'admin']:
            return True

        return False


class GuestReadUserFull(BasePermissionWithType):
    """
    Гости: только чтение публичных данных
    Пользователи: полный доступ к своим данным
    Админы/модераторы: полный доступ ко всему
    """
    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)

        # Все аутентифицированные имеют доступ
        if user_type != 'anonymous':
            return True

        # Анонимы - только безопасные методы публичных данных
        if request.method in permissions.SAFE_METHODS:
            # Проверяем, является ли view публичным
            if hasattr(view, 'is_public_endpoint'):
                return view.is_public_endpoint
            # Или проверяем по имени view
            public_views = ['PostListView', 'PublicProfileView', 'CommentListView']
            return view.__class__.__name__ in public_views

        return False


class ContentAccessPermission(BasePermissionWithType):
    """
    Комплексные права для контента:
    - Гости: чтение публичного
    - Пользователи: чтение всего + создание/редактирование своего
    - Модераторы: чтение всего + редактирование любого
    - Админы: полный доступ
    """
    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)

        # Разрешенные методы для каждого типа
        allowed_methods = {
            'anonymous': ['GET', 'HEAD', 'OPTIONS'],
            'guest': ['GET', 'HEAD', 'OPTIONS', 'POST'],  # Гости могут создавать комментарии
            'user': ['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'moderator': ['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'admin': ['GET', 'HEAD', 'OPTIONS', 'POST', 'PUT', 'PATCH', 'DELETE'],
        }

        return request.method in allowed_methods.get(user_type, [])

    def has_object_permission(self, request, view, obj):
        user_type = self.get_user_type(request.user)

        # Для безопасных методов - всем
        if request.method in permissions.SAFE_METHODS:
            # Проверяем, публичный ли объект
            if hasattr(obj, 'is_public'):
                return obj.is_public or user_type != 'anonymous'
            return True

        # Для изменения/удаления
        if user_type == 'user':
            # Пользователь может изменять только свои объекты
            return hasattr(obj, 'user') and obj.user == request.user
        elif user_type == 'moderator':
            # Модераторы могут изменять любые объекты, кроме определенных
            protected_models = ['User', 'SiteSettings']  # Защищенные модели
            return obj.__class__.__name__ not in protected_models
        elif user_type == 'admin':
            # Админы могут все
            return True

        return False


# apps/accounts/permissions.py
class ModelAccessPermission(BasePermissionWithType):
    """
    Гибкие права доступа к моделям
    Можно настроить для каждой модели отдельно
    """

    # Конфигурация прав по моделям
    MODEL_PERMISSIONS = {
        'Post': {
            'anonymous': ['read_public'],
            'guest': ['read_all', 'create_comment'],
            'user': ['read_all', 'create', 'update_own', 'delete_own'],
            'moderator': ['read_all', 'create', 'update_any', 'delete_any'],
            'admin': ['full_access'],
        },
        'Profile': {
            'anonymous': ['read_public'],
            'guest': ['read_all'],
            'user': ['read_all', 'update_own'],
            'moderator': ['read_all', 'update_any'],
            'admin': ['full_access'],
        },
        'Comment': {
            'anonymous': ['read_public'],
            'guest': ['read_all', 'create'],
            'user': ['read_all', 'create', 'update_own', 'delete_own'],
            'moderator': ['read_all', 'create', 'update_any', 'delete_any'],
            'admin': ['full_access'],
        },
    }

    def has_permission(self, request, view):
        user_type = self.get_user_type(request.user)
        model_name = self._get_model_name(view)

        if model_name not in self.MODEL_PERMISSIONS:
            # По умолчанию разрешаем чтение всем
            return request.method in permissions.SAFE_METHODS

        permissions_list = self.MODEL_PERMISSIONS[model_name].get(user_type, [])

        # Маппинг методов на права
        method_to_permission = {
            'GET': 'read_all' if user_type != 'anonymous' else 'read_public',
            'POST': 'create',
            'PUT': 'update_own',
            'PATCH': 'update_own',
            'DELETE': 'delete_own',
        }

        required_permission = method_to_permission.get(request.method)

        if not required_permission:
            return False

        # Проверяем права
        if required_permission in permissions_list:
            return True

        # Для update_own/delete_own проверяем в has_object_permission
        if required_permission in ['update_own', 'delete_own']:
            return 'update_own' in permissions_list or 'delete_own' in permissions_list

        return False

    def has_object_permission(self, request, view, obj):
        user_type = self.get_user_type(request.user)

        # Для безопасных методов
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'is_public'):
                return obj.is_public or user_type != 'anonymous'
            return True

        # Для изменения/удаления
        if user_type == 'user':
            # Проверяем владение объектом
            if hasattr(obj, 'user'):
                return obj.user == request.user
            elif hasattr(obj, 'author'):
                return obj.author == request.user
            elif hasattr(obj, 'created_by'):
                return obj.created_by == request.user

        return super().has_object_permission(request, view, obj)

    def _get_model_name(self, view):
        """Получает имя модели из view"""
        if hasattr(view, 'queryset'):
            return view.queryset.model.__name__
        elif hasattr(view, 'model'):
            return view.model.__name__
        elif hasattr(view, 'serializer_class'):
            return view.serializer_class.Meta.model.__name__
        return view.__class__.__name__.replace('View', '').replace('ViewSet', '')


class AllowGuests(permissions.BasePermission):
    """
    Разрешает доступ как аутентифицированным пользователям, так и гостям
    """
    def has_permission(self, request, view):
        # Если пользователь - гость (имеет guest_id), считаем его аутентифицированным
        return bool(request.user and (
            request.user.is_authenticated or 
            hasattr(request.user, 'guest_id')
        ))
