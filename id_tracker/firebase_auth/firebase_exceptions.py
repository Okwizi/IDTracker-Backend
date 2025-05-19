"""accounts/firebase_auth/firebase_exceptions.py"""

from rest_framework import status
from rest_framework.exceptions import APIException


class NoAuthToken(APIException):
    """Exception raised when no authentication token is provided."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "No authentication token provided."
    default_code = "no_auth_token"


class InvalidAuthToken(APIException):
    """Exception raised when the authentication token is invalid."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid authentication token provided."
    default_code = "invalid_auth_token"


class FirebaseError(APIException):
    """Exception raised when there is an error with Firebase."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "The user provided with auth token isn't a firebase user."
    default_code = "no_firebase_uid"


class EmailVerification(APIException):
    """Exception raised when the email is not verified."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email not verified."
    default_code = "email_not_verified"
