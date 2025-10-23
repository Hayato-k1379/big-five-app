from __future__ import annotations

from django.conf import settings
_LEGAL_SLUGS = {
    "privacy": "privacy",
    "terms": "terms",
    "disclaimer": "disclaimer",
    "tokushoho": "tokushoho",
}


def _legal_url(slug: str) -> str:
    path = f"/legal/{slug}/"
    site_base = getattr(settings, "SITE_BASE_URL", "").rstrip("/")
    return f"{site_base}{path}" if site_base else path


def app_links(request):
    """Provide absolute URLs for key application entry points."""

    links = {
        "APP_SURVEY_URL": settings.SPA_SURVEY_URL,
    }

    for key, slug in _LEGAL_SLUGS.items():
        links[f"APP_{key.upper()}_URL"] = _legal_url(slug)

    return links
