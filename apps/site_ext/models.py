import uuid
from django.db import models
from django.contrib.sites.models import Site
from core.models import BaseModel
from django.utils.translation import ugettext_lazy as _


class SiteExt(BaseModel):
    """Every site must have token for security reasons
    """
    site = models.OneToOneField(Site, related_name='site_ext', null=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    callback_url = models.URLField(blank=True, null=True)
