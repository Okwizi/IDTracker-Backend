"""Models."""

from django.db import models

from id_tracker.common.models import BaseModel


class Notifications(BaseModel):
    """Notifications model"""

    student_email = models.CharField(max_length=100)
    title = models.CharField(
        max_length=100,
    )
    message = models.TextField()
