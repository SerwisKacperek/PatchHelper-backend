from rest_framework import serializers
from .models import Patch

class PatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patch
        fields = (
            'id', 
            'title', 
            'description',
            'owner',
            'created'
        )