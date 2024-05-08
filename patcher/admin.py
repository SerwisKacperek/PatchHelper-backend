from django.contrib import admin
from .models import Patch

class PatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created')
    list_filter = ['created']
    search_fields = ['title']

admin.site.register(Patch, PatchAdmin)
