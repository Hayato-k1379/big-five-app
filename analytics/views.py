from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import EventLog


def _sid(request: HttpRequest) -> Optional[str]:
    return request.COOKIES.get("anon_sid")


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
    EventLog.objects.create(
        event_type="purchase_note",
        session_id=_sid(request),
        referrer=request.META.get("HTTP_REFERER", ""),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        extra_payload={"path": request.path},
    )
    return render(request, "analytics/purchased_thanks.html", {})
