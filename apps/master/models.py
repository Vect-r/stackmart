from django.db import models
import uuid
# https://docs.djangoproject.com/en/6.0/ref/models/fields/
# Create your models here.
class BaseClass(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True