from django.db import models


class BaseManager(models.Manager):
    """ Base Manager for Base model
    """
    def get_queryset(self):
        return super(BaseManager, self).get_queryset().filter(trashed=False)


class BaseModel(models.Model):
    """Base model storing created_at and updated_at
    """
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, db_index=True)
    trashed = models.BooleanField(default=False, blank=True)

    objects = BaseManager()

    def delete(self, **kwargs):
        self._forced_delete = kwargs.pop('forced', False)
        if not self._forced_delete:
            model = self.__class__
            kwargs.update({'trashed': True})
            model.objects.using(self._db).filter(
                    pk=self.id).update(**kwargs)
        else:
            super(BaseModel, self).delete(**kwargs)


    class Meta:
        abstract = True
