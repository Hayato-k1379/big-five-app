"""Admin registrations for survey models."""
from __future__ import annotations

from django.contrib import admin

from .models import PersonalityItem, SurveyResult


@admin.register(PersonalityItem)
class PersonalityItemAdmin(admin.ModelAdmin):
    list_display = ("code", "trait", "is_reversed", "order")
    list_filter = ("trait", "is_reversed")
    search_fields = ("code", "text_ja")
    ordering = ("order",)


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "created_at",
        "sum_O",
        "sum_C",
        "sum_E",
        "sum_A",
        "sum_N",
    )
    readonly_fields = (
        "uuid",
        "created_at",
        "raw_scores",
        "sum_O",
        "sum_C",
        "sum_E",
        "sum_A",
        "sum_N",
        "scaled_O",
        "scaled_C",
        "scaled_E",
        "scaled_A",
        "scaled_N",
    )
    ordering = ("-created_at",)
    list_filter = ("created_at",)
