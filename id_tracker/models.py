"""Models."""

from django.db import models


class Admin(models.Model):
    """Admin model"""

    admin_name = models.CharField(db_column="admin_name", max_length=200)
    admin_id = models.IntegerField(db_column="admin_id", primary_key=True)

    class Meta:
        """Admin options"""

        db_table = "admin"


class Course(models.Model):
    """Course model"""

    course_id = models.IntegerField(db_column="course_id", primary_key=True)
    dept_id = models.ForeignKey(
        "Departments", models.DO_NOTHING, db_column="dept_id"
    )
    course_name = models.CharField(db_column="course_name", max_length=200)
    school = models.ForeignKey(
        "Schools", models.DO_NOTHING, db_column="school_id"
    )

    class Meta:
        """Course options"""

        db_table = "course"


class Departments(models.Model):
    """Department model"""

    dept_id = models.IntegerField(db_column="dept_id", primary_key=True)
    school = models.ForeignKey(
        "Schools", models.DO_NOTHING, db_column="school_id"
    )
    department_names = models.CharField(
        db_column="department_names", max_length=200
    )

    class Meta:
        """Department options"""

        db_table = "departments"


class Schools(models.Model):
    """School model"""

    school_id = models.IntegerField(db_column="school_id", primary_key=True)
    school_name = models.CharField(db_column="school_name", max_length=200)

    class Meta:
        """School options"""

        db_table = "schools"


# Student Table
class Students(models.Model):
    """Student model"""

    student_first_name = models.CharField(
        db_column="student_first_name", max_length=200
    )
    student_last_name = models.CharField(
        db_column="student_last_name", max_length=200
    )
    full_name = models.CharField(max_length=400, editable=True)
    uid = models.CharField(editable=True, unique=True, max_length=100)
    student_email = models.CharField(
        db_column="student_email", max_length=200, unique=True
    )
    student_reg_no = models.CharField(
        db_column="student_reg_no", primary_key=True, max_length=200
    )
    course = models.CharField(db_column="course", max_length=200)
    contact = models.IntegerField(db_column="contact")
    course_id = models.ForeignKey(
        Course, models.DO_NOTHING, db_column="course_id"
    )
    dept_id = models.ForeignKey(
        Departments, models.DO_NOTHING, db_column="dept_id"
    )
    school = models.ForeignKey(
        Schools, models.DO_NOTHING, db_column="school_id"
    )
    status = models.BooleanField(max_length=100, default=True)
    personal_email = models.CharField(
        db_column="personal_email", max_length=200, default="N/A"
    )

    class Meta:
        """Student options"""

        db_table = "students"

    def save(self, *args, **kwargs):  # noqa
        """Save method."""
        self.full_name = f"{self.student_first_name} {self.student_last_name}"
        super().save(*args, **kwargs)


class Notifications(models.Model):
    """Notifications model"""

    student_email = models.CharField(primary_key=True, max_length=100)
    notification_title = models.CharField(
        max_length=100, blank=True, null=True
    )
    notification_body = models.TextField()
    short_date = models.DateField(auto_now_add=True)

    class Meta:
        """Notification options"""

        db_table = "notifications"
