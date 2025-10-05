from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.utils.http import url_has_allowed_host_and_scheme

from .models import EventLog


def _sid(request: HttpRequest) -> Optional[str]:
    return request.COOKIES.get("anon_sid")


def _next_url(request: HttpRequest) -> Optional[str]:
    candidate = request.GET.get("next")
    if not candidate:
        return None
    if url_has_allowed_host_and_scheme(candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return candidate
    if candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    return None


@require_GET
def go_note_detail(request: HttpRequest) -> HttpResponse:
    EventLog.objects.create(
        event_type="cta_click",
        session_id=_sid(request),
        referrer=request.META.get("HTTP_REFERER", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        extra_payload={"path": request.path},
    )
    return HttpResponseRedirect(settings.NOTE_DETAIL_URL)


@require_GET
def purchased_note(request: HttpRequest) -> HttpResponse:
    next_url = _next_url(request)
    EventLog.objects.create(
        event_type="purchase_note",
        session_id=_sid(request),
        referrer=request.META.get("HTTP_REFERER", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        extra_payload={k: v for k, v in {"path": request.path, "next": next_url}.items() if v is not None},
    )
    if next_url:
        return HttpResponseRedirect(next_url)
    return render(request, "analytics/purchased_thanks.html", {"next_url": next_url})
