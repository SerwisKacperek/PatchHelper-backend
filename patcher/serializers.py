from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Patch
from .models import LandingPageStat
from .models import Profile

class PatchSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Patch
        fields = '__all__'

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

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(max_length=None, use_url=True, required=False)
    bio = serializers.CharField(max_length=250, allow_blank=True, required=False)
    joined = serializers.DateTimeField(read_only=True, required=False)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'avatar', 'bio', 'joined']
        read_only_fields = ['id', 'joined']

    # def update(self, instance, validated_data):
    #     instance.avatar = validated_data.get('avatar', instance.avatar)
    #     instance.bio = validated_data.get('bio', instance.bio)
    #     instance.save()
    #     return instance