from rest_framework import serializers
from .models import Patch
from .models import LandingPageStat

class PatchSerializer(serializers.ModelSerializer):
    creator_username = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Patch
        fields = '__all__'

class LandingPageStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPageStat
        fields = '__all__'