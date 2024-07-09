from django import forms
from .models import Patch

class PatchForm(forms.ModelForm):
    class Meta:
        model = Patch
        fields = ['title', 'description', 'content']