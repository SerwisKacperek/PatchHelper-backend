from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Patch
from .models import PatchContent
from .models import LandingPageStat
from .models import Profile

class LandingPageStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPageStat
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )

        return user
    
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(max_length=None, use_url=True, required=False)
    bio = serializers.CharField(max_length=250, allow_blank=True, required=False)
    joined = serializers.DateTimeField(read_only=True, required=False)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'avatar', 'bio', 'joined']
        read_only_fields = ['id', 'joined']

class PatchContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatchContent
        fields = ['id', 'type', 'text', 'images', 'order']

class PatchSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Patch
        fields = ['id','title', 'description', 'version', 'updated', 'created', 'user', 'upvotes']
        read_only_fields = ['created', 'user']
    
    def create(self, validated_data):
        content_data = self.initial_data.pop('content')
        patch = Patch.objects.create(**validated_data)
        for content in content_data:
            PatchContent.objects.create(post=patch, **content)
        return patch
