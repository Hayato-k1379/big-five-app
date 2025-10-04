"""Tests for the survey REST API endpoints."""
from __future__ import annotations

import json

from django.test import TestCase
from django.urls import reverse

from survey.models import PersonalityItem, SurveyResult


class SurveyAPITests(TestCase):
    """Ensure the API returns items and scores responses correctly."""

    @classmethod
    def setUpTestData(cls) -> None:
        items: list[PersonalityItem] = []
        for trait in ["O", "C", "E", "A", "N"]:
            for index in range(1, 11):
                items.append(
                    PersonalityItem(
                        code=f"{trait}{index}",
                        text_ja=f"{trait} 特性テキスト {index}",
                        trait=trait,
                        is_reversed=index % 2 == 0,
                        order=len(items) + 1,
                    )
                )
        PersonalityItem.objects.bulk_create(items)

    def test_items_endpoint_returns_all_questions(self) -> None:
        response = self.client.get(reverse("survey_api:items"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 50)
        first_item = payload[0]
        self.assertEqual(first_item["code"], "O1")
        self.assertIn("text", first_item)

    def test_score_endpoint_creates_result(self) -> None:
        responses = {item.code: 4 for item in PersonalityItem.objects.all()}
        response = self.client.post(
            reverse("survey_api:score"),
            data=json.dumps({"responses": responses}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertIn("id", body)
        self.assertEqual(len(body["trait_scores"]), 5)
        self.assertTrue(all("label" in row for row in body["trait_scores"]))
        self.assertTrue(all("display_score" in row for row in body["trait_scores"]))
        self.assertTrue(all("raw_mean" in row for row in body["trait_scores"]))
        self.assertIn("highlights", body)
        highlights = body["highlights"]
        self.assertIn("signature_strength", highlights)
        self.assertIn("signature_caution", highlights)
        self.assertIn("contrast_summary_locked", highlights)
        self.assertTrue(highlights["contrast_summary_locked"])
        self.assertEqual(len(body["raw_scores"]), 50)
        self.assertTrue(
            SurveyResult.objects.filter(pk=body["id"]).exists(),
        )

    def test_result_detail_endpoint_returns_payload(self) -> None:
        result = SurveyResult.objects.create(
            raw_scores={"O1": 5},
            sum_O=5,
            sum_C=5,
            sum_E=5,
            sum_A=5,
            sum_N=5,
            scaled_O=100,
            scaled_C=100,
            scaled_E=100,
            scaled_A=100,
            scaled_N=100,
        )
        response = self.client.get(
            reverse("survey_api:result-detail", kwargs={"pk": result.pk})
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["id"], str(result.pk))
        self.assertEqual(len(body["trait_scores"]), 5)
        self.assertIn("highlights", body)

    def test_score_endpoint_validates_missing_answers(self) -> None:
        responses = {"O1": 4}
        response = self.client.post(
            reverse("survey_api:score"),
            data=json.dumps({"responses": responses}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn("responses", body)
        self.assertEqual(SurveyResult.objects.count(), 0)
