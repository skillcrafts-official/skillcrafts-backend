from django.db.models.query import QuerySet

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.privacy_settings.serializers import (
    ProfilePrivacySettingsSerializer,
    ProfileUserBlacklistSerializer, ProfileUserWhitelistSerializer
)
from apps.privacy_settings.models import ProfilePrivacySettings


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]


class ProfilePrivacySettingsView(BaseModelViewSet):
    queryset = ProfilePrivacySettings.objects.all()
    serializer_class = ProfilePrivacySettingsSerializer
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs) -> Response:
        print(self.serializer_class.__dict__)
        return super().retrieve(request, *args, **kwargs)


class ProfileUserBlacklistView(BaseModelViewSet):
    queryset = ProfilePrivacySettings.objects.all()
    serializer_class = ProfileUserBlacklistSerializer
    lookup_field = 'pk'


class ProfileUserWhitelistView(BaseModelViewSet):
    queryset = ProfilePrivacySettings.objects.all()
    serializer_class = ProfileUserWhitelistSerializer
    lookup_field = 'pk'
