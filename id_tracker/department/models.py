"""Models."""

from django.db import models

from id_tracker.common.models import BaseModel
from id_tracker.school.models import School


class Department(BaseModel):
    """Department model"""

    school = models.ForeignKey(
        School, on_delete=models.PROTECT, related_name="departments"
    )
    department_name = models.CharField(max_length=200)
