"""Admin registrations for survey models."""
from __future__ import annotations

import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

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
        "memo",
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
        "radar_chart",
    )
    fields = (
        "uuid",
        "memo",
        "created_at",
        "radar_chart",
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
        "raw_scores",
    )
    ordering = ("-created_at",)
    list_filter = ("created_at",)
    search_fields = ("uuid", "memo")

    def radar_chart(self, obj: SurveyResult) -> str:
        """Render a small radar chart for scaled scores."""

        if not obj:
            return ""

        labels = ["開放性", "誠実性", "外向性", "協調性", "神経症傾向"]
        scores = [
            obj.scaled_O,
            obj.scaled_C,
            obj.scaled_E,
            obj.scaled_A,
            obj.scaled_N,
        ]
        chart_id = f"radar-chart-{obj.pk}"
        labels_json = mark_safe(json.dumps(labels, ensure_ascii=False))
        scores_json = mark_safe(json.dumps(scores))

        return format_html(
            '<div style="max-width: 420px;">'
            '<canvas id="{chart_id}" aria-label="レーダーチャート" role="img"></canvas>'
            '<script>(function(){{'
            "const labels = {labels};"
            "const data = {scores};"
            'const ctx = document.getElementById("{chart_id}");'
            "if (!ctx) return;"
            "const render = () => new Chart(ctx, {{"
            'type: "radar",'
            "data: {{"
            "labels: labels,"
            "datasets: [{{"
            'label: "スコア (0-100)",'
            "data: data,"
            'backgroundColor: "rgba(54, 162, 235, 0.2)",'
            'borderColor: "rgba(54, 162, 235, 1)",'
            'pointBackgroundColor: "rgba(54, 162, 235, 1)"'
            "}}]"
            "}},"
            "options: {{"
            "responsive: true,"
            "plugins: {{ legend: {{ display: false }} }},"
            "scales: {{ r: {{ suggestedMin: 0, suggestedMax: 100, ticks: {{ stepSize: 20 }} }} }}"
            "}}"
            "}});"
            "if (window.Chart) {{"
            "render();"
            "}} else {{"
            "const s = document.createElement('script');"
            "s.src = 'https://cdn.jsdelivr.net/npm/chart.js';"
            "s.onload = render;"
            "document.body.appendChild(s);"
            "}}"
            "}})();</script>"
            "</div>",
            chart_id=chart_id,
            labels=labels_json,
            scores=scores_json,
        )

    radar_chart.short_description = "レーダーチャート"
