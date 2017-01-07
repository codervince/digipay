from django.contrib import admin
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from django.contrib.sites.models import Site
from .models import SiteExt


class SiteExtInline(admin.TabularInline):
    """Extend default site admin with site extension
    """
    model = SiteExt


class SiteAdmin(BaseSiteAdmin):
    list_display = ['domain', 'name', 'token']
    inlines = [SiteExtInline]

    def token(self, obj):
        try:
            hex = obj.site_ext.token.hex
        except SiteExt.DoesNotExist:
            site_ext = SiteExt(site=obj)
            site_ext.save()
            hex = obj.site_ext.token.hex
        return hex


admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)
