"""Models."""

from django.db import models

from id_tracker.common.models import BaseModel


class School(BaseModel):
    """School model"""

    school_name = models.CharField(max_length=200)
