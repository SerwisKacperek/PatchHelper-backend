from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import PatchViewSet
from .views import LandingPageStatViewSet
from .views import PatchDetail

from .views import UserCreate
from .views import LogoutView

# router = DefaultRouter()
# router.register(r'patches', PatchViewSet)
# router.register(r"LandingPageStat", LandingPageStatViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('patches/', PatchViewSet.as_view(), name='patch-list'),
    path('LandingPageStat/', LandingPageStatViewSet.as_view(), name='landing-page-stat'),
    path('patches/<str:title>/', PatchDetail.as_view(), name='patch-detail'),

    path('register/', UserCreate.as_view(), name='user-create'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
]