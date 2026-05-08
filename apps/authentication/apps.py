from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'

    def ready(self):
        try:
            # pylint: disable=import-outside-toplevel,unused-import
            from apps.authentication import spectaculars  # noqa: F401
            # from apps.authentication import signals       # noqa: F401
            # from apps.authentication import handlers      # noqa: F401
        except ImportError:
            pass
