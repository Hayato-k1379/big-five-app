import uuid


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
