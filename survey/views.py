"""View logic for the Big Five survey application."""
from __future__ import annotations

import json

from django.conf import settings
from django.forms.boundfield import BoundField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import SurveyForm
from .models import PersonalityItem, SurveyResult

from .constants import MAX_SCORE, MIN_SCORE, TRAIT_LABELS, TRAIT_ORDER
from .services import SurveyScoringError, create_survey_result


def home(request: HttpRequest) -> HttpResponse:
    """Render the landing page."""
    base_url = settings.SITE_BASE_URL or request.build_absolute_uri("/")
    context = {"site_base_url": base_url.rstrip("/")}
    return render(request, "home.html", context)


def survey(request: HttpRequest) -> HttpResponse:
    """Display the questionnaire and handle submissions."""
    items = list(PersonalityItem.objects.all())
    if not items:
        return render(request, "survey/empty.html")

    if request.method == "POST":
        form = SurveyForm(items=items, data=request.POST)
        if form.is_valid():
            try:
                result = create_survey_result(items, form.cleaned_data)
            except SurveyScoringError:
                form.add_error(None, "回答の集計に失敗しました。もう一度お試しください。")
            else:
                return redirect(reverse("survey:result", kwargs={"pk": result.pk}))
    else:
        form = SurveyForm(items=items)

    question_fields = _build_question_fields(form, items)
    return render(
        request,
        "survey/survey.html",
        {"form": form, "question_fields": question_fields},
    )


def result(request: HttpRequest, pk: str) -> HttpResponse:
    """Show the computed outcome for a completed survey."""
    survey_result = get_object_or_404(SurveyResult, pk=pk)
    trait_rows = [
        {
            "key": trait,
            "label": TRAIT_LABELS[trait],
            "sum": survey_result.trait_sum_map[trait],
            "scaled": survey_result.trait_scaled_map[trait],
        }
        for trait in TRAIT_ORDER
    ]

    chart_data = {
        "labels": [row["label"] for row in trait_rows],
        "scaled": [row["scaled"] for row in trait_rows],
    }

    context = {
        "result": survey_result,
        "trait_rows": trait_rows,
        "chart_json": json.dumps(chart_data, ensure_ascii=False),
        "raw_min": MIN_SCORE,
        "raw_max": MAX_SCORE,
        "scaled_min": 0,
        "scaled_max": 100,
    }
    return render(request, "survey/result.html", context)

def _build_question_fields(form: SurveyForm, items: list[PersonalityItem]) -> list[tuple[PersonalityItem, BoundField]]:
    """Pair each item with its rendered form field for template rendering."""
    return [(item, form[item.code]) for item in items]


def spa_entry(request: HttpRequest) -> HttpResponse:
    """Serve the built Vue application for /app routes."""

    index_path = settings.FRONTEND_DIST_DIR / "index.html"
    if not index_path.exists():
        return HttpResponse(
            "フロントエンドのビルドがまだ実行されていません。`npm run build` 後に再度アクセスしてください。",
            content_type="text/plain",
            status=503,
        )

    return HttpResponse(index_path.read_text(encoding="utf-8"), content_type="text/html")
