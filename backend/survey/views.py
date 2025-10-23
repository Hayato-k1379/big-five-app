"""View logic for the Big Five survey application."""
from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

LEGAL_PAGE_FILES = {
    "privacy": "privacy.html",
    "terms": "terms.html",
    "disclaimer": "disclaimer.html",
    "tokushoho": "tokushoho.html",
}

LEGAL_PUBLIC_DIR = Path(settings.PROJECT_ROOT) / "frontend" / "public"


def home(request: HttpRequest) -> HttpResponse:
    """Render the landing page."""
    base_url = settings.SITE_BASE_URL or request.build_absolute_uri("/")
    context = {"site_base_url": base_url.rstrip("/")}
    return render(request, "home.html", context)


def survey(request: HttpRequest) -> HttpResponse:
    """Redirect legacy entry point to the SPA survey experience."""
    return redirect(settings.SPA_SURVEY_URL)


def result(request: HttpRequest, pk: str) -> HttpResponse:
    """Redirect legacy result pages to the SPA result view."""
    target = f"{settings.SPA_RESULT_BASE_URL}/{pk}"
    return redirect(target)


def spa_entry(request: HttpRequest) -> HttpResponse:
    """Serve the built Vue application for /app routes."""
    return render(
        request,
        "survey/spa_unbuilt.html",
        status=200,
    )


def legal_page(request: HttpRequest, page: str) -> HttpResponse:
    """Serve the static legal documents from the shared public directory."""

    filename = LEGAL_PAGE_FILES.get(page)
    if not filename:
        raise Http404("Unknown legal document.")

    file_path = LEGAL_PUBLIC_DIR / filename
    if not file_path.exists():
        raise Http404("Legal document is not available on this server.")

    content = file_path.read_text(encoding="utf-8")
    return HttpResponse(content, content_type="text/html; charset=utf-8")
