from rest_framework import serializers
from .models import Post
from .models import LandingPageStat

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class LandingPageStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPageStat
        fields = '__all__'