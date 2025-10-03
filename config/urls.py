"""Top-level URL configuration for the Big-Five survey app."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("survey.api.urls")),
    path("", include("survey.urls")),
]
