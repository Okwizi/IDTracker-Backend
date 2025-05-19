"""URLs"""

from django.contrib import admin
from django.urls import path

from id_tracker import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth-status/", views.auth_status, name="auth-status"),
    path("fetch-user-data/", views.fetch_user_data, name="fetch_user_data"),
    path("edit-user-data/", views.edit_user_data, name="edit_user_data"),
    path("check-auth/", views.check_auth, name="check-auth"),
    path("status/", views.status, name="status"),
    path(
        "send-notification/", views.send_notification, name="send-notification"
    ),
    path("get-notification/", views.get_notification, name="get-notification"),
    # path('api/register/',views.registerTwoFactor, name='register_two_factor')
    # path('api/register/', views.register, name='register'),
    # path('api/verify/', views.verify, name='verify'),
    # path('api/validate/', views.validate, name='validate'),
]
