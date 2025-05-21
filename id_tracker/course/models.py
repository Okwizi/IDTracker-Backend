"""Models."""

from django.db import models

from id_tracker.common.models import BaseModel
from id_tracker.department.models import Department
from id_tracker.school.models import School


class Course(BaseModel):
    """Course model"""

    course_name = models.CharField(max_length=200)
    department = models.ForeignKey(
        Department, models.PROTECT, related_name="courses"
    )
    school = models.ForeignKey(School, models.PROTECT, related_name="courses")
