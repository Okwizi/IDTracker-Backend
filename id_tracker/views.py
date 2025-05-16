import json

import firebase_admin

# from django.contrib.sessions.backends.db import SessionStore
# from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.http import JsonResponse

# from django.views.decorators.http import require_POST
from firebase_admin import auth, credentials

from id_tracker.firebase_auth.firebase_exceptions import FirebaseError
from id_tracker.models import Notifications, Students

# Firebase Admin SDK credentials
try:
    cred = credentials.Certificate(
        "idtrackr-firebase-adminsdk-i1ceu-bcac716f78.json"
    )
    firebase_admin.initialize_app(cred)
except Exception:
    raise FirebaseError("Firebase Admin SDK credentials not found.")


def auth_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            authenticated = data.get("authenticated")
            email = data.get("email")
            print("STATUS:", authenticated)
            print("email:", email)

            if authenticated:
                request.session["student_email"] = email
                # Retrieve user data from Firebase Authentication
                user_data = get_user_data(email)
                if user_data:
                    print("User Data:", user_data)
                    increment_user_profile_columns(user_data)
                    return JsonResponse(
                        {"message": "User data processed successfully"},
                        status=200,
                    )
                else:
                    return JsonResponse(
                        {
                            "error": "User data not found in Firebase Authentication"
                        },
                        status=400,
                    )
            else:
                return JsonResponse(
                    {"error": "This user is not authenticated."},
                    status=400,
                )
        except json.JSONDecodeError as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"}, status=400
        )


def get_user_data(email):
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
        return print("Error finding Email !!")


def increment_user_profile_columns(user_data):
    """Get an existing UserProfile instance based on the email."""
    try:
        user_profile = Students.objects.get(
            student_email=user_data["student_email"]
        )

        for key, value in user_data.items():
            if getattr(user_profile, key) != value:
                setattr(user_profile, key, value)

        user_profile.save()
    except Students.DoesNotExist:
        raise Exception(Students.DoesNotExist)


def check_auth(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            data.get("authenticated")

            return JsonResponse(
                {"message": "User is authenticated"}, status=200
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"}, status=400
        )


def fetch_user_data(request):
    """Fetch student data based on the provided email."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse(
                    {"error": "Email not provided"}, status=400
                )

            try:
                user_profile = Students.objects.get(student_email=email)
            except Students.DoesNotExist:
                return JsonResponse(
                    {"error": "User data not found"}, status=404
                )

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

            return JsonResponse(user_data, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"}, status=405
        )


def status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            status = data.get("status_value")
            email = data.get("email")
            print("ID STATUS:", status + " " + email)

            student = Students.objects.get(student_email=email)

            if status == "True":
                student.status = True
            elif status == "False":
                student.status = False
            else:
                # TODO: Handle invalid status value here
                pass

            student.save()

            return JsonResponse(
                {"message": "Data received successfully"}, status=200
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"}, status=400
        )


def send_notification(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_email = data.get("email")

            try:
                Students.objects.get(student_email=student_email)
            except Students.DoesNotExist:
                return JsonResponse({"error": "Student not found"}, status=404)

            # TODO: Formulate notifications better than this
            notification_title = "IDTrackr Notification"
            notification_body = "Your ID has been recovered and can be collected at the Administrator's office."

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

            return JsonResponse({"success": True}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"}, status=400
        )


def get_notification(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            student_email = data.get("email")

            try:
                student = Students.objects.get(student_email=student_email)
            except Students.DoesNotExist:
                return JsonResponse({"error": "Student not found"}, status=404)

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
                return JsonResponse(
                    {"message": "No notifications available"}, status=200
                )
            else:
                return JsonResponse(
                    {"notifications": notification_list}, status=200
                )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"}, status=400
        )


def edit_user_data(request):
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

                return JsonResponse(
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
                return JsonResponse({"error": "Student not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"}, status=400
        )


# -------------------------------------------------------------------
# views.py
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
# import uuid
# import base64
# import pyotp
# import qrcode
# from io import BytesIO

# from PIL import Image
# from .models import User  # Import your User model

# @csrf_exempt
# def register(request):
#     if request.method == 'POST':
#         id = uuid.uuid4()
#         try:
#             # Create temporary secret until it is verified
#             temp_secret = pyotp.random_base32()
#             # Generate OTP auth URL
#             otpauth_url = pyotp.totp.TOTP(temp_secret).provisioning_uri(str(id), issuer_name="IDTrackr")
#             # Generate QR code
#             qr_image = generate_qr_code(otpauth_url)
#             # Create user in the database
#             user = User.objects.create(id=id, temp_secret=temp_secret, qr_image=qr_image)
#             return JsonResponse({'id': str(id), 'qrImage': qr_image, 'setupKey': temp_secret})
#         except Exception as e:
#             print(e)
#             return JsonResponse({'message': 'Error generating secret key'}, status=500)

# @csrf_exempt
# def verify(request):
#     if request.method == 'POST':
#         data = request.POST
#         user_id = data.get('userId')
#         token = data.get('token')
#         try:
#             # Retrieve user from database
#             user = User.objects.get(id=user_id)
#             # Verify token
#             totp = pyotp.TOTP(user.temp_secret)
#             if totp.verify(token):
#                 # Update user data
#                 user.secret = user.temp_secret
#                 user.save()
#                 return JsonResponse({'verified': True})
#             else:
#                 return JsonResponse({'verified': False})
#         except Exception as e:
#             print(e)
#             return JsonResponse({'message': 'Error retrieving user'}, status=500)

# @csrf_exempt
# def validate(request):
#     if request.method == 'POST':
#         data = request.POST
#         user_id = data.get('userId')
#         token = data.get('token')
#         try:
#             # Retrieve user from database
#             user = User.objects.get(id=user_id)
#             # Validate token
#             totp = pyotp.TOTP(user.secret)
#             if totp.verify(token):
#                 return JsonResponse({'validated': True})
#             else:
#                 return JsonResponse({'validated': False})
#         except Exception as e:
#             print(e)
#             return JsonResponse({'message': 'Error retrieving user'}, status=500)

# def generate_qr_code(data):
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)
#     img = qr.make_image(fill_color="black", back_color="white")
#     buffered = BytesIO()
#     img.save(buffered, format="PNG")
#     img_str = base64.b64encode(buffered.getvalue()).decode()
#     return img_str
