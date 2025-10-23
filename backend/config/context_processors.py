from __future__ import annotations

from django.conf import settings
from django.urls import reverse

_APP_PATHS = {
    "survey": ("/app/survey", "survey:survey"),
    "privacy": ("/app/privacy", "survey:legal-page", {"page": "privacy"}),
    "terms": ("/app/terms", "survey:legal-page", {"page": "terms"}),
    "disclaimer": ("/app/disclaimer", "survey:legal-page", {"page": "disclaimer"}),
    "tokushoho": ("/app/legal/tokushoho", "survey:legal-page", {"page": "tokushoho"}),
}


def _resolve_app_link(path: str, fallback_name: str, kwargs: dict | None = None) -> str:
    origin = getattr(settings, "FRONTEND_ORIGIN", "")
    if origin:
        return f"{origin.rstrip('/')}{path}"
    url = reverse(fallback_name, kwargs=kwargs)
    site_base = getattr(settings, "SITE_BASE_URL", "").rstrip("/")
    if site_base:
        return f"{site_base}{url}"
    return url


def app_links(request):
    """Provide SPA entry links with graceful fallback to server-rendered routes."""

    resolved = {}
    for key, spec in _APP_PATHS.items():
        path, name, *rest = spec
        kwargs = rest[0] if rest else None
        resolved[f"APP_{key.upper()}_URL"] = _resolve_app_link(path, name, kwargs)
    return resolved
