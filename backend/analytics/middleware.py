import hashlib
import logging
import uuid
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class EnsureSessionIdMiddleware:
    COOKIE_NAME = "anon_sid"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.COOKIES.get(self.COOKIE_NAME):
            request._set_new_sid = str(uuid.uuid4())
        response = self.get_response(request)
        if getattr(request, "_set_new_sid", None):
            # Persist for one year with SameSite=Lax to keep analytics scoped to this site
            response.set_cookie(
                self.COOKIE_NAME,
                request._set_new_sid,
                max_age=60 * 60 * 24 * 365,
                samesite="Lax",
            )
        return response


class LogLandingPageViewMiddleware:
    """Record landing page pageviews on the server side."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.landing_paths = tuple(getattr(settings, "ANALYTICS_LP_PATHS", ("/",)))
        self.ip_salt = getattr(settings, "ANALYTICS_IP_HASH_SALT", settings.SECRET_KEY)

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._maybe_log(request, response)
        except Exception:
            logger.exception("Failed to log page view")
        return response

    def _maybe_log(self, request, response):
        if request.method not in {"GET", "HEAD"}:
            return

        path = request.path
        if path not in self.landing_paths:
            return

        from analytics.models import PageView

        PageView.objects.create(
            path=path,
            method=request.method,
            status_code=getattr(response, "status_code", 0) or 0,
            referrer=request.META.get("HTTP_REFERER", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            ip_hash=self._hash_ip(self._client_ip(request)),
            session_id=request.COOKIES.get(EnsureSessionIdMiddleware.COOKIE_NAME)
            or getattr(request, "_set_new_sid", None),
        )

    def _client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            parts = [part.strip() for part in forwarded_for.split(",") if part.strip()]
            if parts:
                return parts[0]
        return request.META.get("REMOTE_ADDR", "")

    def _hash_ip(self, ip: Optional[str]):
        if not ip:
            return ""
        salt = self.ip_salt or ""
        return hashlib.sha256(f"{salt}:{ip}".encode("utf-8")).hexdigest()
