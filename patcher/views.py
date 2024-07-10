from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, generics

from .models import Patch
from .models import LandingPageStat
from .serializers import PatchSerializer
from .serializers import LandingPageStatSerializer
from .forms import PatchForm

class PatchViewSet(generics.ListAPIView):
    queryset = Patch.objects.all().order_by('created')
    serializer_class = PatchSerializer

class PatchDetail(generics.RetrieveAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
    lookup_field = 'title'

class LandingPageStatViewSet(generics.ListAPIView):
    queryset = LandingPageStat.objects.all()
    serializer_class = LandingPageStatSerializer

def index(request):
    return render(request, 'index.html')

def patch_detail(request, title=None):
    return render(request, 'index.html', {'title': title})