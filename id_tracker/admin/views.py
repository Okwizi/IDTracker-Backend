"""Views"""

import base64
import json
import logging
import uuid
from io import BytesIO

import firebase_admin
import pyotp
import qrcode

# from django.contrib.sessions.backends.db import SessionStore
# from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

# from django.views.decorators.http import require_POST
from firebase_admin import auth, credentials
from rest_framework.request import Request
from rest_framework.response import Response

from id_tracker.firebase_auth.firebase_exceptions import FirebaseError
from id_tracker.models import Notifications, Students

from .models import User

LOGGING = logging.getLogger(__name__)
# Firebase Admin SDK credentials
try:
    cred = credentials.Certificate(
        "idtrackr-firebase-adminsdk-i1ceu-bcac716f78.json"
    )
    firebase_admin.initialize_app(cred)
except FirebaseError:
    raise


def auth_status(request: Request) -> Response:
    """Check if the user is authenticated and retrieve user data."""
    if request.method == "POST":
        try:
            authenticated = request.get("authenticated")
            email = request.get("email")

            if authenticated:
                request.session["student_email"] = email
                # Retrieve user data from Firebase Authentication
                user_data = get_user_data(email)
                if user_data:
                    increment_user_profile_columns(user_data)
                    return Response(
                        {"message": "User data processed successfully"},
                        status=200,
                    )
                else:
                    return Response(
                        {"error": "User data not found"},
                        status=400,
                    )
            else:
                return Response(
                    {"error": "This user is not authenticated."},
                    status=400,
                )
        except json.JSONDecodeError as e:
            LOGGING.error(f"JSON decode error: {e}")
            return Response({"error": "An error occurred"}, status=400)
    else:
        return Response(
            {"error": "Only POST requests are allowed"}, status=400
        )


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


def increment_user_profile_columns(user_data: dict) -> None:
    """Get an existing UserProfile instance based on the email."""
    try:
        user_profile = Students.objects.get(
            student_email=user_data["student_email"]
        )

        for key, value in user_data.items():
            if getattr(user_profile, key) != value:
                setattr(user_profile, key, value)

        user_profile.save()
    except (Students.DoesNotExist, Exception):
        raise


def check_auth(request: Request) -> Response:
    """Check if the user is authenticated."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            data.get("authenticated")

            return Response({"message": "User is authenticated"}, status=200)

        except Exception as e:
            LOGGING.error(f"Error checking authentication: {e}")
            return Response({"error": "Error checking Auth"}, status=400)

    else:
        return Response(
            {"error": "Only POST requests are allowed"}, status=400
        )


def fetch_user_data(request: Request) -> Response:
    """Fetch student data based on the provided email."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return Response({"error": "Email not provided"}, status=400)

            try:
                user_profile = Students.objects.get(student_email=email)
            except Students.DoesNotExist:
                return Response({"error": "User data not found"}, status=404)

            user_data = {
                "full_name": (
                    user_profile.full_name if user_profile.full_name else ""
                ),
                "reg_no": (
                    user_profile.student_reg_no
                    if user_profile.student_reg_no
                    else ""
                ),
                "contact": user_profile.contact,
                "student_email": user_profile.student_email,
                "personal_email": user_profile.personal_email,
                "dept": (
                    user_profile.dept_id.dept_id
                    if user_profile.dept_id
                    else ""
                ),
                "school": (
                    user_profile.school.school_id
                    if user_profile.school
                    else ""
                ),
                "course": user_profile.course if user_profile.course else "",
                "status": user_profile.status if user_profile.status else "",
            }

            return Response(user_data, status=200)

        except Exception as e:
            LOGGING.error(f"Error fetching user data: {e}")
            return Response({"error": "Error fetching user data"}, status=500)

    else:
        return Response(
            {"error": "Only POST requests are allowed"}, status=405
        )


def status(request: Request) -> Response:
    """Check the status of a student."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            status = data.get("status_value")
            email = data.get("email")

            student = Students.objects.get(student_email=email)

            if status == "True":
                student.status = True
            elif status == "False":
                student.status = False
            else:
                # TODO: Handle invalid status value here
                pass

            student.save()

            return Response(
                {"message": "Data received successfully"}, status=200
            )

        except Exception as e:
            LOGGING.error(f"Error checking status: {e}")
            return Response({"error": "Error retrieving status"}, status=400)

    else:
        return Response(
            {"error": "Only POST requests are allowed"}, status=400
        )


def send_notification(request: Request) -> Response:
    """Send a notification to the student when their ID is recovered."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_email = data.get("email")

            try:
                Students.objects.get(student_email=student_email)
            except Students.DoesNotExist:
                return Response({"error": "Student not found"}, status=404)

            # TODO: Formulate notifications better than this
            notification_title = "IDTrackr Notification"
            notification_body = (
                "Your ID has been recovered and can "
                "be collected at the Administrator's office."
            )

            # create a new notification instance associated with the student
            new_notification = Notifications.objects.create(
                student_email=student_email,
                notification_title=notification_title,
                notification_body=notification_body,
            )

            # sending email notification
            admin_email = "okwizitest@gmail.com"
            send_mail(
                new_notification.notification_title,
                new_notification.notification_body,
                admin_email,
                [student_email],
                fail_silently=False,
            )

            return Response({"success": True}, status=200)
        except Exception as e:
            LOGGING.error(f"Error sending notification: {e}")
            return Response(
                {"error": "Error sending notification"}, status=400
            )
    else:
        return Response(
            {"error": "Only POST requests are allowed"}, status=400
        )


def get_notification(request: Request) -> Response:
    """Get notifications for a specific student based on the provided email."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_email = data.get("email")

            try:
                student = Students.objects.get(student_email=student_email)
            except Students.DoesNotExist:
                return Response({"error": "Student not found"}, status=404)

            # filter notifications based on the student's email
            notifications = Notifications.objects.filter(
                student_email=student.student_email
            )

            # serialize notifications
            notification_list = []
            for notification in notifications:
                notification_list.append(
                    {
                        "notification_title": notification.notification_title,
                        "notification_body": notification.notification_body,
                        "short_date": notification.short_date,
                    }
                )

            if len(notification_list) == 0:
                return Response(
                    {"message": "No notifications available"}, status=200
                )
            else:
                return Response(
                    {"notifications": notification_list}, status=200
                )
        except Exception as e:
            LOGGING.error(f"Error getting notification: {e}")
            return Response(
                {"error": "Error getting notification"}, status=400
            )
    else:
        return Response(
            {"error": "Only POST requests are allowed"}, status=400
        )


def edit_user_data(request: Request) -> Response:
    """Edit user data based on the provided email."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            contact = data.get("contact")
            personal_email = data.get("personal_email")

            try:
                student = Students.objects.get(student_email=email)

                student.contact = contact
                student.personal_email = personal_email
                student.save()

                return Response(
                    {
                        "message": "Data updated successfully",
                        "updated_data": {
                            "contact": contact,
                            "personal_email": personal_email,
                        },
                    },
                    status=200,
                )

            except Students.DoesNotExist:
                return Response({"error": "Student not found"}, status=404)

        except Exception as e:
            LOGGING.error(f"Error editing user data: {e}")
            return Response({"error": "Error editing user data"}, status=400)

    else:
        return Response(
            {"error": "Only POST requests are allowed"}, status=400
        )


@csrf_exempt
def register(request: Request) -> Response:
    """Register a new user and generate a QR code for OTP setup."""
    id = uuid.uuid4()
    try:
        # Create temporary secret until it is verified
        temp_secret = pyotp.random_base32()
        # Generate OTP auth URL
        otpauth_url = pyotp.totp.TOTP(temp_secret).provisioning_uri(
            str(id), issuer_name="IDTrackr"
        )
        # Generate QR code
        qr_image = generate_qr_code(otpauth_url)
        # Create user in the database
        User.objects.create(id=id, temp_secret=temp_secret, qr_image=qr_image)
        return Response(
            {"id": str(id), "qrImage": qr_image, "setupKey": temp_secret}
        )
    except Exception:
        return Response({"message": "Error generating secret key"}, status=500)


@csrf_exempt
def verify(request: Request) -> Response | None:
    """Verify the OTP token provided by the user."""
    if request.method == "POST":
        data = request.POST
        user_id = data.get("userId")
        token = data.get("token")
        try:
            # Retrieve user from database
            user = User.objects.get(id=user_id)
            # Verify token
            totp = pyotp.TOTP(user.temp_secret)
            if totp.verify(token):
                # Update user data
                user.secret = user.temp_secret
                user.save()
                return Response({"verified": True})
            else:
                return Response({"verified": False})
        except Exception:
            return Response({"message": "Error retrieving user"}, status=500)


@csrf_exempt
def validate(request: Request) -> Response | None:
    """Validate the OTP token provided by the user."""
    if request.method == "POST":
        data = request.POST
        user_id = data.get("userId")
        token = data.get("token")
        try:
            # Retrieve user from database
            user = User.objects.get(id=user_id)
            # Validate token
            totp = pyotp.TOTP(user.secret)
            if totp.verify(token):
                return Response({"validated": True})
            else:
                return Response({"validated": False})
        except Exception:
            return Response({"message": "Error retrieving user"}, status=500)


def generate_qr_code(data: dict) -> str:
    """Generate a QR code from the given data and return a base64 string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str
