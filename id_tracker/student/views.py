"""Views"""

import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from id_tracker.student.models import Students
from id_tracker.student.utilities import (
    get_user_data,
    increment_user_profile_columns,
)

LOGGING = logging.getLogger(__name__)


@action(methods=["POST"], detail=True)
def auth_status(request: Request) -> Response:
    """Check if the user is authenticated."""
    authenticated = request.get("authenticated")
    email = request.get("email")

    if authenticated:
        # retrieve user data from Firebase Authentication
        user_data = get_user_data(email)
        if user_data:
            increment_user_profile_columns(user_data)
            return Response(
                {"message": "User data processed successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "User data not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"error": "This user is not authenticated."},
            status=status.HTTP_404_NOT_FOUND,
        )


@action(methods=["POST"], detail=True)
def fetch_user_data(request: Request) -> Response:
    """Fetch student data based on the provided email."""
    try:
        email = request.data.get("email", None)

        if not email:
            return Response(
                {"error": "Email not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_profile = Students.objects.get(student_email=email)
        except Students.DoesNotExist:
            return Response(
                {"error": "Student not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_data = {
            "full_name": (user_profile.full_name or ""),
            "reg_no": (user_profile.student_reg_no or ""),
            "contact": user_profile.phone,
            "student_email": user_profile.email,
            "dept": (user_profile.department.id),
            "school": (user_profile.school.id),
            "course": user_profile.course,
            "status": user_profile.status,
        }

        return Response(user_data, status=status.HTTP_200_OK)

    except Exception as e:
        LOGGING.error(f"Error fetching user data: {e}")
        return Response(
            {"error": "Error fetching user data"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@action(methods=["POST"], detail=True)
def student_status(request: Request) -> Response:
    """Check the status of a student."""
    try:
        fe_status = request.data.get("status_value", None)
        email = request.data.get("email")

        student = Students.objects.get(student_email=email)

        if fe_status == "True":
            student.status = True
        elif fe_status == "False":
            student.status = False
        else:
            raise ValueError("Invalid status value provided")

        student.save()

        return Response(
            {"message": "Data received successfully"},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        LOGGING.error(f"Error checking status: {e}")
        return Response(
            {"error": "Error retrieving status"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@action(methods=["POST"], detail=True)
def edit_user_data(request: Request) -> Response:
    """Edit user data based on the provided email."""
    email = request.data.get("email")
    phone = request.data.get("phone")

    try:
        student = Students.objects.get(student_email=email)

        student.phone = phone
        student.email = email
        student.save()

        return Response(
            {
                "message": "Data updated successfully",
                "updated_data": {
                    "phone": phone,
                    "email": email,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Students.DoesNotExist:
        return Response(
            {"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND
        )
