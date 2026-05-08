from typing import Any

from rest_framework import viewsets


class ProfileBlacklistViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    
    def get_object(self) -> Any:
        return super().get_object()