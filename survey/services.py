"""Domain services for scoring the Big Five survey."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .constants import MAX_SCORE, MIN_SCORE, TRAIT_ORDER
from .models import PersonalityItem, SurveyResult


class SurveyScoringError(ValueError):
    """Raised when incoming responses cannot be scored."""


@dataclass(frozen=True)
class ComputedScores:
    """Holds intermediate scoring results."""

    raw_scores: dict[str, int]
    trait_sums: dict[str, int]
    scaled_scores: dict[str, int]


def scale_score(total: int) -> int:
    """Convert a raw 10-50 total score into a 0-100 scale."""
    scaled = (total - MIN_SCORE) / (MAX_SCORE - MIN_SCORE) * 100
    return max(0, min(100, round(scaled)))


def compute_trait_scores(
    items: Iterable[PersonalityItem],
    responses: Mapping[str, int | str],
) -> ComputedScores:
    """Aggregate trait scores from the provided responses."""

    item_list = list(items)
    if not item_list:
        raise SurveyScoringError("No personality items are registered.")

    raw_scores: dict[str, int] = {}
    trait_sums: dict[str, int] = {trait: 0 for trait in TRAIT_ORDER}

    for item in item_list:
        if item.code not in responses:
            raise SurveyScoringError(f"Missing response for item {item.code}.")
        value = _coerce_answer(responses[item.code], code=item.code)
        raw_scores[item.code] = value
        adjusted = 6 - value if item.is_reversed else value
        trait_sums[item.trait] += adjusted

    scaled_scores = {trait: scale_score(total) for trait, total in trait_sums.items()}
    return ComputedScores(raw_scores=raw_scores, trait_sums=trait_sums, scaled_scores=scaled_scores)


def create_survey_result(
    items: Iterable[PersonalityItem],
    responses: Mapping[str, int | str],
) -> SurveyResult:
    """Persist a scored survey submission and return the saved model."""

    computed = compute_trait_scores(items, responses)
    trait_sums = computed.trait_sums
    scaled = computed.scaled_scores

    return SurveyResult.objects.create(
        raw_scores=computed.raw_scores,
        sum_O=trait_sums["O"],
        sum_C=trait_sums["C"],
        sum_E=trait_sums["E"],
        sum_A=trait_sums["A"],
        sum_N=trait_sums["N"],
        scaled_O=scaled["O"],
        scaled_C=scaled["C"],
        scaled_E=scaled["E"],
        scaled_A=scaled["A"],
        scaled_N=scaled["N"],
    )


def _coerce_answer(value: int | str, *, code: str) -> int:
    try:
        numeric = int(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive branch
        raise SurveyScoringError(f"Invalid response for item {code}.") from exc

    if numeric < 1 or numeric > 5:
        raise SurveyScoringError(f"Response for item {code} must be between 1 and 5.")
    return numeric
