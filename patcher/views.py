from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Patch
from .models import LandingPageStat
from .models import Profile

from .serializers import PatchSerializer
from .serializers import LandingPageStatSerializer
from .serializers import UserSerializer
from .serializers import ProfileSerializer

from .forms import PatchForm

import logging
logger = logging.getLogger(__name__)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CurrentProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
class ProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = self.get_queryset().get(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

def index(request):
    return render(request, 'index.html')

def patch_detail(request, title=None):
    return render(request, 'index.html', {'title': title})