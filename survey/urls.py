"""URL routing for the survey app."""
from django.urls import path, re_path

from . import views

app_name = "survey"

urlpatterns = [
    path("", views.home, name="home"),
    path("survey/", views.survey, name="survey"),
    path("result/<uuid:pk>/", views.result, name="result"),
    path("app/", views.spa_entry, name="app"),
    re_path(r"^app/.+", views.spa_entry, name="app-catchall"),
]
