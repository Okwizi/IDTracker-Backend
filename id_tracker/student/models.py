"""Student app models."""

from django.db import models

from id_tracker.common.models import UserModel
from id_tracker.course.models import Course
from id_tracker.department.models import Department
from id_tracker.school.models import School


class Students(UserModel):
    """Student model"""

    student_reg_no = models.CharField(
        primary_key=True, unique=True, max_length=200
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name="students"
    )
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="students"
    )
    school = models.ForeignKey(
        School, on_delete=models.PROTECT, related_name="students"
    )
    status = models.BooleanField(max_length=100, default=True)

    def __str__(self) -> str:
        """String representation of the student."""
        return f"{self.first_name} {self.last_name} ({self.student_reg_no})"

    @property
    def full_name(self) -> str:
        """Get the full name of the student."""
        return f"{self.first_name} {self.last_name}"
