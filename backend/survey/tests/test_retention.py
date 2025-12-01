"""Tests for retention and scrubbing of survey results."""
from __future__ import annotations

from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from survey.models import SurveyResult


def _create_result(raw_scores: dict, created_delta_days: int) -> SurveyResult:
    result = SurveyResult.objects.create(
        raw_scores=raw_scores,
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
    created_at = timezone.now() - timedelta(days=created_delta_days)
    SurveyResult.objects.filter(pk=result.pk).update(created_at=created_at)
    return SurveyResult.objects.get(pk=result.pk)


@override_settings(SURVEY_RESULT_RETENTION_DAYS=10, SURVEY_RESULT_SCRUB_RAW_AFTER_DAYS=5)
class RetentionCommandTests(TestCase):
    def test_purge_command_scrubs_and_deletes(self) -> None:
        recent = _create_result({"O1": 3}, created_delta_days=2)
        scrub_candidate = _create_result({"O1": 4}, created_delta_days=6)
        delete_candidate = _create_result({"O1": 5}, created_delta_days=12)

        call_command("purge_old_results")

        self.assertTrue(SurveyResult.objects.filter(pk=recent.pk).exists())
        recent.refresh_from_db()
        self.assertEqual(recent.raw_scores, {"O1": 3})

        scrub_candidate.refresh_from_db()
        self.assertEqual(scrub_candidate.raw_scores, {})

        self.assertFalse(SurveyResult.objects.filter(pk=delete_candidate.pk).exists())
