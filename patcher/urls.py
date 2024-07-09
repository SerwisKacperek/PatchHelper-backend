from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatchViewSet
from .views import LandingPageStatViewSet

router = DefaultRouter()
router.register(r'patches', PatchViewSet)
router.register(r"LandingPageStat", LandingPageStatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]