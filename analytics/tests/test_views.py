from django.test import TestCase, override_settings
from django.urls import reverse

from analytics.middleware import EnsureSessionIdMiddleware
from analytics.models import EventLog


@override_settings(NOTE_DETAIL_URL="https://example.com/premium")
class AnalyticsViewTests(TestCase):
    def test_go_note_detail_logs_event_and_redirects(self) -> None:
        cookie_value = "test-session-id"
        self.client.cookies[EnsureSessionIdMiddleware.COOKIE_NAME] = cookie_value

        url = reverse("go_note_detail")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://example.com/premium")

        event = EventLog.objects.get()
        self.assertEqual(event.event_type, "cta_click")
        self.assertEqual(event.session_id, cookie_value)
        self.assertEqual(event.extra_payload, {"path": url})

    def test_purchased_note_logs_event_and_renders_thank_you(self) -> None:
        url = reverse("purchased_note")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "analytics/purchased_thanks.html")
        self.assertContains(response, "ご購入ありがとうございます")

        event = EventLog.objects.get()
        self.assertEqual(event.event_type, "purchase_note")
        self.assertIsNone(event.session_id)
        self.assertEqual(event.extra_payload, {"path": url})

        # Middleware should attach a cookie when none was provided.
        self.assertIn(EnsureSessionIdMiddleware.COOKIE_NAME, response.cookies)
