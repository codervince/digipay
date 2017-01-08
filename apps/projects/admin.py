from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'token')
    list_filter = ('created_at',)

    def token(self, obj):
        return obj.token.hex
