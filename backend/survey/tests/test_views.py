"""Regression tests for public-facing survey routes."""
from __future__ import annotations

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class SurveyRoutingTests(TestCase):
    def test_home_page_renders(self) -> None:
        response = self.client.get(reverse("survey:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_survey_route_redirects_to_spa(self) -> None:
        response = self.client.get(reverse("survey:survey"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], settings.SPA_SURVEY_URL)

    def test_result_route_redirects_to_spa(self) -> None:
        fake_pk = "12345678-1234-1234-1234-123456789012"
        response = self.client.get(reverse("survey:result", kwargs={"pk": fake_pk}))
        self.assertEqual(response.status_code, 302)
        expected = f"{settings.SPA_RESULT_BASE_URL}/{fake_pk}"
        self.assertEqual(response.headers["Location"], expected)


class LegalPageTests(TestCase):
    def test_privacy_page_served(self) -> None:
        response = self.client.get(reverse("survey:legal-page", kwargs={"page": "privacy"}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("プライバシーポリシー".encode("utf-8"), response.content)
