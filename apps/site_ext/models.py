import uuid
from django.db import models
from django.db.models import signals
from django.contrib.sites.models import Site
from core.models import BaseModel
from django.utils.translation import ugettext_lazy as _

class SiteExt(BaseModel):
    """Every site must have token for security reasons
    """
    site = models.OneToOneField(Site, related_name='site_ext', null=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, null=True)


def create_ext(sender, instance, created, **kwargs):
    """Create SiteExt for every new Site."""
    if created:
        SiteExt.objects.create(site=instance)

signals.post_save.connect(create_ext, sender=Site, weak=False,
                          dispatch_uid='models.create_ext')
