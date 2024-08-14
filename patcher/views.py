from django.shortcuts import render, get_list_or_404
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
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

class UserPatchViewSet(generics.ListAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
    pagination_class = PatchPagination

    filter_backends = [OrderingFilter]
    
    def get(self, request):
        id = request.query_params.get('user_id')
        if id:
            posts = Patch.objects.filter(user_id=id)
        else:
            # the user is not authenticated
            if not self.request.user.is_authenticated:
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            posts = Patch.objects.filter(user=request.user)

        paginator = PatchPagination()
        serializer = PatchSerializer(posts, many=True)
        page = paginator.paginate_queryset(posts, request)
        return paginator.get_paginated_response(data=serializer.data)

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

class UserViewset(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'id'

    permission_classes_by_action = {'get': [AllowAny]}

    def get(self, request):
        id = request.query_params.get('user_id')
        
        if id:
            user = User.objects.get(id=id)
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        else: # if user_id was not specified, return the current user
            if not self.request.user.is_authenticated:
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            user = User.objects.get(id=request.user.id)
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)

class CurrentProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if not self.request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
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