from rest_framework import generics
from .models import Patch
from .serializers import PatchSerializer

class PatchList(generics.ListCreateAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer

class PatchDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer
