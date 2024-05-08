from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from patcher import views

urlpatterns = [
    path('patches/', views.PatchList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)