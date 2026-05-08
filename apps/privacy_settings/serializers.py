"""Serializers for $PATH_TO_APP"""
from django.db import transaction

from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.privacy_settings.models import ProfilePrivacySettings
from apps.accounts.models import User


class ProfilePrivacySettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfilePrivacySettings
        # fields = '__all__'
        exclude = ['profile']
        read_only_fields = ['blacklist', 'whitelist']


class ProfileUserBlacklistSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(
        write_only=True,
        required=True,
        choices=[('block', 'block'), ('unblock', 'unblock')]
    )
    for_user_id = serializers.IntegerField(write_only=True)
    success = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProfilePrivacySettings
        fields = ['action', 'for_user_id', 'success', 'blacklist']
        read_only_fields = ['blacklist']

    def update(self, instance, validated_data):
        action = validated_data.get('action', None)
        for_user_id = validated_data.get('for_user_id', None)

        if for_user_id == self.context['request'].user.id:
            raise ValidationError()

        if for_user_id is None:
            return instance

        with transaction.atomic():
            user = User.objects.filter(id=for_user_id).first()
            if not user:
                return instance

            if action == 'block':
                if not instance.blacklist.filter(id=for_user_id).exists():
                    instance.blacklist.add(user)
            elif action == 'unblock':
                if instance.blacklist.filter(id=for_user_id).exists():
                    instance.blacklist.remove(user)
            else:
                raise ValidationError()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['success'] = True
        return representation


class ProfileUserWhitelistSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(
        write_only=True,
        required=True,
        choices=[('filter', 'filter'), ('exclude', 'exclude')]
    )
    for_user_id = serializers.IntegerField(write_only=True)
    success = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProfilePrivacySettings
        fields = ['action', 'for_user_id', 'success', 'whitelist']
        read_only_fields = ['whitelist']

    def update(self, instance, validated_data):
        action = validated_data.get('action', None)
        for_user_id = validated_data.get('for_user_id', None)

        if for_user_id == self.context['request'].user.id:
            raise ValidationError()

        if for_user_id is None:
            return instance

        with transaction.atomic():
            user = User.objects.filter(id=for_user_id).first()
            if not user:
                return instance

            if action == 'filter':
                if not instance.whitelist.filter(id=for_user_id).exists():
                    instance.whitelist.add(user)
            elif action == 'exclude':
                if instance.whitelist.filter(id=for_user_id).exists():
                    instance.whitelist.remove(user)
            else:
                raise ValidationError()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['success'] = True
        return representation
