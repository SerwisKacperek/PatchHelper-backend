from django.shortcuts import render
from rest_framework import viewsets
from .models import Patch
from .serializers import PatchSerializer

class PatchView(viewsets.ModelViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
