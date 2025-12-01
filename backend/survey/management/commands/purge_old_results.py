"""Management command to scrub or delete old survey results based on retention policy."""
from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from survey.models import SurveyResult


class Command(BaseCommand):
    help = "Scrub raw answers and delete survey results according to retention settings."

    def handle(self, *args, **options):
        now = timezone.now()
        scrub_days = max(0, int(getattr(settings, "SURVEY_RESULT_SCRUB_RAW_AFTER_DAYS", 0)))
        retention_days = max(0, int(getattr(settings, "SURVEY_RESULT_RETENTION_DAYS", 0)))

        scrubbed = 0
        deleted = 0

        if scrub_days:
            scrub_cutoff = now - timedelta(days=scrub_days)
            scrub_qs = SurveyResult.objects.filter(created_at__lt=scrub_cutoff).exclude(raw_scores={})
            scrubbed = scrub_qs.update(raw_scores={})

        if retention_days:
            delete_cutoff = now - timedelta(days=retention_days)
            deleted, _ = SurveyResult.objects.filter(created_at__lt=delete_cutoff).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Purged survey results: scrubbed={scrubbed}, deleted={deleted}, "
                f"scrub_days={scrub_days}, retention_days={retention_days}"
            )
        )
