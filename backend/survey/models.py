"""Database models for the Big Five personality survey."""
from __future__ import annotations

from uuid import uuid4

from django.db import models


class PersonalityItem(models.Model):
    """Represents a single IPIP Big Five item."""

    class Trait(models.TextChoices):
        OPENNESS = "O", "O"
        CONSCIENTIOUSNESS = "C", "C"
        EXTRAVERSION = "E", "E"
        AGREEABLENESS = "A", "A"
        NEUROTICISM = "N", "N"

    code = models.CharField(max_length=8, unique=True)
    text_ja = models.TextField()
    trait = models.CharField(max_length=1, choices=Trait.choices)
    is_reversed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.code}: {self.text_ja[:40]}"


class SurveyResult(models.Model):
    """Stores aggregated scores for a single survey submission."""

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    raw_scores = models.JSONField(help_text="Keyed by item code (E1, A1, ...) with the original 1-5 answers")
    sum_O = models.PositiveSmallIntegerField()
    sum_C = models.PositiveSmallIntegerField()
    sum_E = models.PositiveSmallIntegerField()
    sum_A = models.PositiveSmallIntegerField()
    sum_N = models.PositiveSmallIntegerField()
    scaled_O = models.PositiveSmallIntegerField()
    scaled_C = models.PositiveSmallIntegerField()
    scaled_E = models.PositiveSmallIntegerField()
    scaled_A = models.PositiveSmallIntegerField()
    scaled_N = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"SurveyResult {self.uuid}"

    @property
    def trait_sum_map(self) -> dict[str, int]:
        return {
            "O": self.sum_O,
            "C": self.sum_C,
            "E": self.sum_E,
            "A": self.sum_A,
            "N": self.sum_N,
        }

    @property
    def trait_scaled_map(self) -> dict[str, int]:
        return {
            "O": self.scaled_O,
            "C": self.scaled_C,
            "E": self.scaled_E,
            "A": self.scaled_A,
            "N": self.scaled_N,
        }
