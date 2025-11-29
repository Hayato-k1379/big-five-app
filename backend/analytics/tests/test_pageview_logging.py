import hashlib

from django.conf import settings
from django.test import TestCase

from analytics.models import PageView


class PageViewLoggingTests(TestCase):
    def test_logs_root_page_view(self):
        response = self.client.get("/", HTTP_X_FORWARDED_FOR="203.0.113.5")

        self.assertEqual(response.status_code, 200)
        pv = PageView.objects.get()
        self.assertEqual(pv.path, "/")
        self.assertEqual(pv.method, "GET")
        self.assertEqual(pv.status_code, 200)
        expected_hash = hashlib.sha256(f"{settings.SECRET_KEY}:203.0.113.5".encode("utf-8")).hexdigest()
        self.assertEqual(pv.ip_hash, expected_hash)
        self.assertIsNotNone(pv.session_id)

    def test_ignores_non_landing_paths(self):
        self.client.get("/survey/")
        self.assertEqual(PageView.objects.count(), 0)

    def test_does_not_log_post_requests(self):
        self.client.post("/")
        self.assertEqual(PageView.objects.count(), 0)
