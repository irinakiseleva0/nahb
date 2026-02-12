from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("django.contrib.auth.urls")),  # login/logout/password reset
    path("accounts/", include("accounts.urls")),             # signup

    path("stories/", include("stories.urls")),
]
