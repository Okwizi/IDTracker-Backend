"""Common app models."""

from django.db import models


class BaseModel(models.Model):
    """Common abstract model."""

    id = models.UUIDField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        """Meta options."""

        abstract = True
        ordering = ["-created_at"]


class UserModel(BaseModel):
    """User model."""

    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True)
