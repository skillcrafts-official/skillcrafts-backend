from django.apps import AppConfig


class ConsentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.consents'

    def ready(self):
        try:
            # pylint: disable=import-outside-toplevel,unused-import
            from apps.consents import spectaculars  # noqa: F401
            # from apps.consents import signals       # noqa: F401
            # from apps.consents import handlers      # noqa: F401
        except ImportError:
            pass
