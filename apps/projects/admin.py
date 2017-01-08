from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_code')
    list_filter = ('created_at',)

    def project_code(self, obj):
        return obj.code.hex
