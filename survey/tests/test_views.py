"""Integration tests for survey views and scoring."""
from __future__ import annotations

import json

from django.test import TestCase
from django.urls import reverse

from survey.models import PersonalityItem, SurveyResult


class SurveyViewEmptyTests(TestCase):
    """Ensure empty state is handled when no items exist."""

    def test_survey_page_shows_empty_template(self) -> None:
        response = self.client.get(reverse("survey:survey"))
        self.assertTemplateUsed(response, "survey/empty.html")
        self.assertContains(response, "設問がまだ登録されていません")


class SurveyFlowTests(TestCase):
    """Full-stack tests covering form rendering, submission, and results."""

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

    def test_home_page_renders(self) -> None:
        response = self.client.get(reverse("survey:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "IPIP Big Five 50問テスト")

    def test_survey_page_lists_all_questions(self) -> None:
        response = self.client.get(reverse("survey:survey"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "survey/survey.html")
        # Expect first question label to appear
        first_item = PersonalityItem.objects.order_by("order").first()
        assert first_item is not None
        self.assertContains(response, first_item.text_ja)

    def test_successful_submission_creates_result_with_scaled_scores(self) -> None:
        post_data = {
            item.code: "4"
            for item in PersonalityItem.objects.all()
        }

        response = self.client.post(reverse("survey:survey"), data=post_data, follow=False)
        self.assertEqual(response.status_code, 302)
        result = SurveyResult.objects.get()
        expected_sum = 30  # 5 normal (4) + 5 reversed (6-4=2)
        self.assertEqual(result.sum_O, expected_sum)
        self.assertEqual(result.sum_C, expected_sum)
        self.assertEqual(result.sum_E, expected_sum)
        self.assertEqual(result.sum_A, expected_sum)
        self.assertEqual(result.sum_N, expected_sum)
        expected_scaled = 50
        self.assertEqual(result.scaled_O, expected_scaled)
        self.assertEqual(result.scaled_C, expected_scaled)
        self.assertEqual(result.scaled_E, expected_scaled)
        self.assertEqual(result.scaled_A, expected_scaled)
        self.assertEqual(result.scaled_N, expected_scaled)

        # Result view renders correctly
        result_url = reverse("survey:result", kwargs={"pk": result.pk})
        response = self.client.get(result_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "survey/result.html")
        self.assertContains(response, "診断結果")
        chart_json = response.context["chart_json"]
        payload = json.loads(chart_json)
        self.assertEqual(payload["scaled"], [expected_scaled] * 5)

    def test_invalid_submission_shows_errors(self) -> None:
        # leave out one required field
        items = list(PersonalityItem.objects.order_by("order"))
        post_data = {item.code: "3" for item in items[:-1]}
        response = self.client.post(reverse("survey:survey"), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "survey/survey.html")
        self.assertContains(response, "この項目は必須です。", html=False)
        self.assertFalse(SurveyResult.objects.exists())
