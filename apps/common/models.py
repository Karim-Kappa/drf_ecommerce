import uuid
from django.db import models
from django.utils import timezone

from apps.common.managers import GetOrNoneManager, GetOrNoneQuerySet


class BaseModel(models.Model):
    """
    A base model class that includes common fields and methods for all models.

    Attributes:
        id (UUIDField): Unique identifier for the model instance.
        created_at (DateTimeField): Timestamp when the instance was created.
        updated_at (DateTimeField): Timestamp when the instance was last updated.
    """

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GetOrNoneManager()

    class Meta:
        abstract = True



class IsDeletedQuerySet(GetOrNoneQuerySet):
    def delete(self, hard_delete=False):
        if hard_delete:
            return super().delete()
        else:
            return self.update(is_deleted=True, deleted_at=timezone.now())


class IsDeletedManager(GetOrNoneManager):
    def get_queryset(self):
        return IsDeletedQuerySet(self.model).filter(is_deleted=False)

    def unfiltered(self):
        return IsDeletedQuerySet(self.model)

    def hard_delete(self):
        return self.unfiltered().delete(hard_delete=True)


class IsDeletedModel(BaseModel):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-id']   # New
        abstract = True

    objects = IsDeletedManager()

    def delete(self, *args, **kwargs):
        # Мягкое удаление is_deleted=True
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

