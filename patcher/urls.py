from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PatchViewSet
from .views import LandingPageStatViewSet
from .views import PatchDetail

# router = DefaultRouter()
# router.register(r'patches', PatchViewSet)
# router.register(r"LandingPageStat", LandingPageStatViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('patches/', PatchViewSet.as_view(), name='patch_list'),
    path('LandingPageStat/', LandingPageStatViewSet.as_view(), name='landing_page_stat'),
    path('patches/<str:title>/', PatchDetail.as_view(), name='patch_detail'),
]