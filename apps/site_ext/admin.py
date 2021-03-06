from django.contrib import admin
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from django.contrib.sites.models import Site
from .models import SiteExt


class SiteExtInline(admin.StackedInline):
    """Extend default site admin with site extension
    """
    model = SiteExt
    fields = ('api_key', 'callback_url')


class SiteAdmin(BaseSiteAdmin):
    list_display = ['domain', 'name', 'token', 'api_key', 'callback_url']
    inlines = [SiteExtInline]

    def api_key(self, obj):
        return obj.site_ext.api_key

    def token(self, obj):
        try:
            hex = obj.site_ext.token.hex
        except SiteExt.DoesNotExist:
            site_ext = SiteExt(site=obj)
            site_ext.save()
            hex = obj.site_ext.token.hex
        return hex

    def callback_url(self, obj):
        return obj.site_ext.callback_url


admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)
