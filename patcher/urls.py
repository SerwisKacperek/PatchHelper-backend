from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# patch views
from .views import PatchViewSet
from .views import PatchUpdateView
from .views import UserPatchViewSet
from .views import PatchContentViewSet
from .views import PatchCreate
from .views import PatchDetail
from .views import upvote_patch

# user views
from .views import LogoutView
from .views import CurrentProfileDetail
from .views import ProfileDetail
from .views import UserViewset

# other views
from .views import LandingPageStatViewSet
from .views import UploadView

urlpatterns = [
    path('patches/', PatchViewSet.as_view(), name='patch-list'),
    path('patches/new/', PatchCreate.as_view(), name='new-patch'),
    path('patches/user/', UserPatchViewSet.as_view(), name='user-patches'),
    path('patches/<uuid>/', PatchDetail.as_view(), name='patch-detail'),
    path('patches/<uuid>/content', PatchContentViewSet.as_view(), name='patch-content'),
    path('patches/<uuid>/upvote/', upvote_patch, name='upvote-patch'),
    path('patches/<uuid>/update/', PatchUpdateView.as_view(), name='update-patch'),

    path('user/', UserViewset.as_view(), name='user-detail'),
    path('register/', UserViewset.as_view(), name='user-create'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('profile/me', CurrentProfileDetail.as_view(), name='current-profile'),
    path('profile/<int:id>', ProfileDetail.as_view(), name='user-profile'),

    path('LandingPageStat/', LandingPageStatViewSet.as_view(), name='landing-page-stat'),
    path('upload/', UploadView.as_view(), name='upload'),

] 