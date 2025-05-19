"""accounts/firebase_auth/firebase_authentication.py"""

import os

import firebase_admin
from firebase_admin import auth, credentials
from rest_framework import authentication
from rest_framework.request import Request

from id_tracker.models import User

from .firebase_exceptions import (
    EmailVerification,
    FirebaseError,
    InvalidAuthToken,
    NoAuthToken,
)

# Firebase Admin SDK credentials
try:
    cred = credentials.Certificate(
        os.getenv("FIREBASE_ADMIN_SDK_CREDENTIALS_PATH")
    )
    default_app = firebase_admin.initialize_app(cred)
except FirebaseError:
    (
        "Firebase Admin SDK credentials not found. "
        "Please add the path to the credentials file to the "
        "FIREBASE_ADMIN_SDK_CREDENTIALS_PATH environment variable."
    )


class FirebaseAuthentication(authentication.BaseAuthentication):
    """Firebase authentication class."""

    keyword = "Bearer"

    def authenticate(self, request: Request) -> tuple | None:
        """Authenticate the user using Firebase authentication."""
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            raise NoAuthToken("No authentication token provided.")

        id_token = auth_header.split(" ").pop()
        decoded_token = None
        try:
            decoded_token = auth.verify_id_token(id_token)
        except InvalidAuthToken:
            "Invalid authentication token provided."

        if not id_token or not decoded_token:
            return None

        email_verified = decoded_token.get("email_verified")
        if not email_verified:
            raise EmailVerification(
                "Email not verified. Please verify your email address."
            )

        try:
            uid = decoded_token.get("uid")
        except FirebaseError:
            ("The user provided with auth token is not a Firebase user.")

        try:
            user = User.objects.get(firebase_uid=uid)
            return (user, None)
        except (User.DoesNotExist, FirebaseError):
            ("The user provided with auth token is not a Firebase user.")
