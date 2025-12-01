"""Serializers for the survey REST API."""
from __future__ import annotations

from rest_framework import serializers

from survey.constants import MAX_SCORE, MIN_SCORE
from survey.models import PersonalityItem
from survey.services import SurveyScoringError, compute_trait_scores
from survey.insights import (
    serialize_highlights,
    serialize_trait_displays,
)


class PersonalityItemSerializer(serializers.ModelSerializer):
    """Expose questionnaire items to the frontend."""

    text = serializers.CharField(source="text_ja")

    class Meta:
        model = PersonalityItem
        fields = ("code", "text", "trait", "is_reversed", "order")


class SurveyScoreRequestSerializer(serializers.Serializer):
    """Validate the payload sent when scoring a survey."""

    responses = serializers.DictField(
        child=serializers.IntegerField(min_value=1, max_value=5),
        allow_empty=False,
    )

    def validate(self, attrs: dict) -> dict:
        items = self.context.get("items")
        if items is None:
            raise AssertionError("API misconfigured without items in context.")

        item_codes = [item.code for item in items]
        responses = attrs["responses"]

        missing = [code for code in item_codes if code not in responses]
        if missing:
            raise serializers.ValidationError(
                {"responses": [f"回答が不足しています: {', '.join(missing)}"]}
            )

        extra = sorted(set(responses.keys()) - set(item_codes))
        if extra:
            raise serializers.ValidationError(
                {"responses": [f"不要な設問コードが含まれています: {', '.join(extra)}"]}
            )

        try:
            compute_trait_scores(items, responses)
        except SurveyScoringError as exc:
            raise serializers.ValidationError({"responses": [str(exc)]}) from exc

        return attrs


def serialize_result_payload(result) -> dict[str, object]:
    """Build the API payload shared by score and detail endpoints."""
    rows, highlights = serialize_trait_displays(result.trait_sum_map)
    return {
        "id": str(result.pk),
        "created_at": result.created_at.isoformat(),
        "trait_scores": rows,
        "raw_range": {"min": MIN_SCORE, "max": MAX_SCORE},
        "scaled_range": {"min": 0, "max": 100},
        "highlights": serialize_highlights(highlights),
    }
