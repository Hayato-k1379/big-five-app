"""Project-level middleware utilities."""
from __future__ import annotations


class AdminContentSecurityPolicyMiddleware:
    """Add a conservative CSP for admin pages to enforce self-hosted assets."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/admin/"):
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
            response.headers.setdefault("Content-Security-Policy", csp)
        return response
