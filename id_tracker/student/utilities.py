"""Student utilities for ID Tracker."""

import logging

from firebase_admin import auth

from id_tracker.firebase_auth.firebase_exceptions import FirebaseError
from id_tracker.student.models import Students

LOGGER = logging.getLogger(__name__)


def get_user_data(email: str) -> dict | None:
    """Retrieve user data from Firebase Authentication based on email."""
    try:
        user = auth.get_user_by_email(email)
        user_data = {
            "uid": user.uid,
            "student_email": user.email,
            "full_name": user.display_name,
        }
        return user_data
    except auth.UserNotFoundError:
        return None
    except FirebaseError as e:
        LOGGER.error(f"Firebase error: {e}")
        raise Exception("An error occurred while fetching user data")


def increment_user_profile_columns(user_data: dict) -> None:
    """Get an existing UserProfile instance based on the email."""
    try:
        student = Students.objects.get(student_email=user_data["email"])

        for key, value in user_data.items():
            if getattr(student, key) != value:
                setattr(student, key, value)

        student.save()
    except (Students.DoesNotExist, Exception):
        LOGGER.error(f"User profile not found or error occurred: {user_data}")
        raise
