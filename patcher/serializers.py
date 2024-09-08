import logging
import json
from rest_framework import serializers
from django.contrib.auth import models as auth_models
from .models import Patch
from .models import PatchContent
from .models import LandingPageStat
from .models import Profile

logger = logging.getLogger(__name__)

class LandingPageStatSerializer(serializers.ModelSerializer):
    """Model Serializer for LandingPageStat model"""
    class Meta:
        model = LandingPageStat
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    """Model Serializer for User model"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = auth_models.User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = auth_models.User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )

        return user

class UserDetailSerializer(serializers.ModelSerializer):
    """Model Serializer for User model"""
    class Meta:
        model = auth_models.User
        fields = ['id', 'username']

class ProfileSerializer(serializers.ModelSerializer):
    """Model Serializer for Profile model"""
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(max_length=None, use_url=True, required=False)
    bio = serializers.CharField(max_length=250, allow_blank=True, required=False)
    joined = serializers.DateTimeField(read_only=True, required=False)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'avatar', 'bio', 'joined']
        read_only_fields = ['id', 'joined']

class PatchContentSerializer(serializers.ModelSerializer):
    """Model Serializer for PatchContent model"""
    class Meta:
        model = PatchContent
        fields = "__all__"

class PatchSerializer(serializers.ModelSerializer):
    """Model Serializer for Patch model"""
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Patch
        fields = "__all__"
        read_only_fields = ['created', 'user', 'uuid']

    def create(self, validated_data):
        try:
            content_data = json.loads(self.initial_data.get('content'))
        except json.JSONDecodeError as exc:
            raise serializers.ValidationError("Content's JSON is invalid", code='invalid') from exc
        except TypeError as exc:
            raise serializers.ValidationError("Content must be a JSON array", code='invalid') from exc

        patch = Patch.objects.create(**validated_data)

        for content in content_data:
            content["post"] = patch.uuid
            content = PatchContentSerializer(data=content)

            if content.is_valid():
                content.save()
            else:
                patch.delete()
                logger.error('Validation errors: %s, %s', content.errors, content.initial_data)
                raise serializers.ValidationError(content.errors)

        return patch

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.thumbnail = validated_data.get('thumbnail', instance.thumbnail)
        instance.version = validated_data.get('version', instance.version)
        instance.state = validated_data.get('state', instance.state)
        instance.save()

        if 'content' in self.initial_data:
            try:
                content_data = json.loads(self.initial_data.get('content'))
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError("Content's JSON is invalid", code='invalid') from exc
            except TypeError as exc:
                raise serializers.ValidationError("Content must be a JSON array", code='invalid') from exc

            for content in content_data:
                content_id = content.get('id', None)

                if content_id:
                    try:
                        content_instance = PatchContent.objects.get(id=content_id)
                    except PatchContent.DoesNotExist as exc:
                        raise serializers.ValidationError("Content ID does not exist", code='invalid') from exc

                    content_instance.type = content.get('type', content_instance.type)
                    content_instance.order = content.get('order', content_instance.order)
                    content_instance.text = content.get('text', content_instance.text)
                    content_instance.images = content.get('images', content_instance.images)
                    content_instance.save()
                else:
                    raise serializers.ValidationError("Content ID must be provided", code='invalid')

        return instance
