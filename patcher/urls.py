from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import PatchViewSet
from .views import LandingPageStatViewSet
from .views import PatchDetail


from .views import UserCreate
from .views import LogoutView
from .views import CurrentProfileDetail
from .views import ProfileDetail
from .views import UserViewset

urlpatterns = [
    path('patches/', PatchViewSet.as_view(), name='patch-list'),
    path('patches/<str:title>/', PatchDetail.as_view(), name='patch-detail'),
    path('LandingPageStat/', LandingPageStatViewSet.as_view(), name='landing-page-stat'),

    path('users/', UserViewset.as_view(), name='user-create'),
    path('register/', UserCreate.as_view(), name='user-create'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('profile/me', CurrentProfileDetail.as_view(), name='profile-detail'),
    path('profile/<int:id>', ProfileDetail.as_view(), name='profile-detail'),
] 