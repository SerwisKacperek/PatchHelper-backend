from django.shortcuts import render, get_list_or_404
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.storage import default_storage
from django.conf import settings
from uuid import UUID
import datetime
import os

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
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

from .exceptions import InvalidUUIDException

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
    ordering_fields = ['created', 'upvotes', 'updated_at']
    ordering = '-created'

    def get_queryset(self):
        queryset = self.queryset.filter(state='published') # only show published patches
        ordering = self.request.query_params.get('ordering', None)

        # Ordering the queryset
        if ordering:
            # Apply ordering if specified
            queryset = queryset.order_by(*ordering.split(','))
        else:
            # Default ordering
            queryset = queryset.order_by(self.ordering)
        
        return queryset
    
    def get(self, request):
        queryset = self.get_queryset()

        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # If pagination is not applied
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserPatchViewSet(generics.ListAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
    pagination_class = PatchPagination

    filter_backends = [OrderingFilter]
    ordering_fields = ['created', 'upvotes', 'updated_at']
    ordering = '-created' 

    def get_queryset(self):
        id = self.request.query_params.get('user_id')
        ordering = self.request.query_params.get('ordering', None)

        # Filetering the queryset based on the user_id
        if id:
            queryset = self.queryset.filter(user__id=id)
        else:
            # the user is not authenticated
            if not self.request.user.is_authenticated:
                raise PermissionDenied()
            
            queryset = self.queryset.filter(user=self.request.user)

        # Ordering the queryset
        if ordering:
            # Apply ordering if specified
            queryset = queryset.order_by(*ordering.split(','))
        else:
            # Default ordering
            queryset = queryset.order_by(self.ordering)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # If pagination is not applied
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class PatchUpdateView(generics.UpdateAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
    lookup_field = 'uuid'

    def patch(self, request, *args, **kwargs):
        # validate the given uuid
        try:
            uuid = UUID(kwargs['uuid'])
        except ValueError:
            raise InvalidUUIDException()

        post = Patch.objects.get(uuid=uuid)

        # check if the user has permission to update the post
        # TODO: add permission classes
        if post.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # check and save the updated data
        serializer = PatchSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.validated_data['updated'] = datetime.datetime.now()
            serializer.save()
            return Response(serializer.data)
        else:
            logger.error(f'Validation errors: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatchCreate(generics.CreateAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer

    def post(self, request, *args, **kwargs):
        serializer = PatchSerializer(data=request.data)

        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        if serializer.is_valid():
            del serializer.validated_data['upvoted_by']
            serializer.validated_data['user'] = request.user

            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f'Validation errors: {serializer.errors}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatchDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
    lookup_field = 'uuid'

class PatchContentViewSet(generics.ListAPIView):
    queryset = PatchContent.objects.all()
    serializer_class = PatchContentSerializer

    def get_queryset(self):
        patch_uuid = self.kwargs['uuid']

        # ensure the uuid is valid
        try:
            patch_uuid = UUID(patch_uuid)
        except ValueError:
            raise InvalidUUIDException()
        
        patch = get_list_or_404(Patch, uuid=patch_uuid)
        return PatchContent.objects.filter(post=patch[0])
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = PatchContentSerializer(queryset, many=True)
        return Response(serializer.data)

class LandingPageStatViewSet(generics.ListAPIView):
    queryset = LandingPageStat.objects.all()
    serializer_class = LandingPageStatSerializer

class UserViewset(generics.ListCreateAPIView):
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
        
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        # check username length
        elif len(request.data.get("username")) < 4:
            return Response({'detail': 'Username must be at least 4 characters long'}, status=status.HTTP_400_BAD_REQUEST)
        elif len(request.data.get("username")) > 25:
            return Response({'detail': 'Username must be at most 25 characters long'}, status=status.HTTP_400_BAD_REQUEST)

        # check password length
        elif len(request.data.get("password")) < 3:
            return Response({'detail': 'Password must be at least 3 characters long'}, status=status.HTTP_400_BAD_REQUEST)
        elif len(request.data.get("password")) > 20:
            return Response({'detail': 'Password must be at most 20 characters long'}, status=status.HTTP_400_BAD_REQUEST)

        # validate email
        try: 
            validate_email(request.data.get("email"))
        except ValidationError:
            return Response({'detail': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentProfileDetail(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
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

class UploadView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_FORBIDDEN)
        
        file = request.FILES.get('file')

        if not file:
            return Response({'detail': 'No file was uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        default_storage.location = os.path.join(settings.MEDIA_ROOT, 'files')
        filename = default_storage.save(file.name, file)
        file_url = os.path.join(os.path.join(settings.MEDIA_URL, "files"), filename)
        absolute_url = request.build_absolute_uri(file_url)

        return Response({'url': absolute_url}, status=status.HTTP_201_CREATED)

def index(request):
    return render(request, 'index.html')

def patch_detail(request, title=None):
    return render(request, 'index.html', {'title': title})

@api_view(['POST'])
def upvote_patch(request, uuid):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    try:
        uuid = UUID(uuid)
    except ValueError:
        raise InvalidUUIDException()

    post = Patch.objects.get(uuid=uuid)
    upvoted = post.upvote(request.user)

    if upvoted:
        return Response({'detail': 'Post succesfully upvoted'}, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Already upvoted'}, status=status.HTTP_400_BAD_REQUEST)
