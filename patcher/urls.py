from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet
from .views import LandingPageStatViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r"LandingPageStat", LandingPageStatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]