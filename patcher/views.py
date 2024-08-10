from django.shortcuts import render, get_list_or_404
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from .pagination import PatchPagination

from .models import Patch
from .models import PatchContent
from .models import LandingPageStat
from .models import Profile

from .serializers import PatchSerializer
from .serializers import PatchContentSerializer
from .serializers import LandingPageStatSerializer
from .serializers import UserSerializer
from .serializers import UserDetailSerializer
from .serializers import ProfileSerializer

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
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
    pagination_class = PatchPagination

    filter_backends = [OrderingFilter]

class PatchCreate(generics.CreateAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PatchContentViewSet(generics.ListAPIView):
    queryset = PatchContent.objects.all()
    serializer_class = PatchContentSerializer

    def get_queryset(self):
        title = self.kwargs['title']
        patch = get_list_or_404(Patch, title=title)
        return PatchContent.objects.filter(post=patch[0])
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = PatchContentSerializer(queryset, many=True)
        return Response(serializer.data)

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

class UserViewset(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'id'

class CurrentUserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user 

class CurrentProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        return self.request.user.profile
    
class ProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
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

@api_view(['POST'])
def upvote_post(request, patch_id):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    post = Patch.objects.get(id=patch_id)
    user = request.user

    if post.upvote(user):
        return Response(PatchSerializer(post).data, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Already upvoted'}, status=status.HTTP_400_BAD_REQUEST)