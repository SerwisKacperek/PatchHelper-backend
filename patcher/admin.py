from django.contrib import admin
from .models import Patch
from .models import LandingPageStat

class PatchesAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')
    list_filter = ['created']
    search_fields = ['title']

class LandingPageStatAdmin(admin.ModelAdmin):
    list_display = ('value', 'description')
    list_filter = ["description"]
    search_fields = ['description']

admin.site.register(Patch, PatchesAdmin)
admin.site.register(LandingPageStat, LandingPageStatAdmin)
