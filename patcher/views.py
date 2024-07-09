from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets
from .models import Patch
from .models import LandingPageStat
from .serializers import PatchSerializer
from .serializers import LandingPageStatSerializer
from .forms import PatchForm

class PatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.all().order_by('created')
    serializer_class = PatchSerializer

@login_required
def create_patch(request):
    if request.method == 'POST':
        form = PatchForm(request.POST)
        if form.is_valid():
            patch = form.save(commit=False)
            patch.creator = request.user
            patch.save()
            return redirect('patcher:patch_detail', pk=patch.pk)
    else:
        form = PatchForm()
    return render(request, 'patcher/new_patch.html', {'form': form})

class LandingPageStatViewSet(viewsets.ModelViewSet):
    queryset = LandingPageStat.objects.all()
    serializer_class = LandingPageStatSerializer

def index(request):
    return render(request, 'index.html')