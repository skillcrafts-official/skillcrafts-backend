"""The viewsets extentions for app auth"""

from django.db import transaction
from django.db.models.query import QuerySet
from django.core.cache import cache

from rest_framework import viewsets, status
from rest_framework.serializers import BaseSerializer
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# class

