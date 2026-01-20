from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.consents.models import UserConsent

from docs.utils import read_md_section


class UserConsentViewSet(viewsets.ModelViewSet):
    queryset = UserConsent.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False, methods=['GET'])
    def get_policy(self, request: Request):
        return Response(data={
            'policy': read_md_section('consents/policy.md')
        })

    @action(detail=False, methods=['GET'])
    def get_personal(self, request: Request):
        return Response(data={
            'personal_data_process': read_md_section('consents/personal_data.md')
        })

