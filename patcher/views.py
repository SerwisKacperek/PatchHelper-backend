from django.shortcuts import render

from rest_framework import viewsets
from .models import Post
from .models import LandingPageStat
from .serializers import PostSerializer
from .serializers import LandingPageStatSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('created')
    serializer_class = PostSerializer

class LandingPageStatViewSet(viewsets.ModelViewSet):
    queryset = LandingPageStat.objects.all()
    serializer_class = LandingPageStatSerializer

def index(request):
    return render(request, 'index.html')