import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from core.models import BaseModel


class Project(BaseModel):
    """Project model
    """
    name = models.CharField(_('Name'), max_length=255, null=True)
    code = models.UUIDField(default=uuid.uuid4, editable=False, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'projects'
