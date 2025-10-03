"""URL configuration for the survey REST API."""
from __future__ import annotations

from django.urls import path

from .views import PersonalityItemListView, SurveyResultDetailView, SurveyScoreView

app_name = "survey_api"

urlpatterns = [
    path("items/", PersonalityItemListView.as_view(), name="items"),
    path("score/", SurveyScoreView.as_view(), name="score"),
    path("results/<uuid:pk>/", SurveyResultDetailView.as_view(), name="result-detail"),
]
