"""Utilities for enriching survey results with display metrics."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

from .constants import MAX_SCORE, MIN_SCORE, TRAIT_LABELS, TRAIT_ORDER

BOOST_FACTOR = 1.3
RANGE_THRESHOLD = 1.0
DISPLAY_SCALE = 12
RAW_MEAN_DECIMALS = 2
Z_DECIMALS = 4


@dataclass(frozen=True)
class TraitDisplay:
    """Computed metrics for a single trait."""

    trait: str
    label: str
    sum_score: int
    raw_mean: float
    z_score: float
    z_boosted: float
    display_score: int

    @property
    def level(self) -> str:
        if self.display_score >= 60:
            return "strong"
        if self.display_score <= 40:
            return "weak"
        return "neutral"


@dataclass(frozen=True)
class HighlightCard:
    trait: str
    label: str
    display_score: int


@dataclass(frozen=True)
class Highlights:
    signature_strength: HighlightCard
    signature_caution: HighlightCard
    strong_candidates: tuple[HighlightCard, ...]
    weak_candidates: tuple[HighlightCard, ...]
    contrast_summary_locked: bool = True


def _scale_to_percentage(total: int) -> float:
    return (total - MIN_SCORE) / (MAX_SCORE - MIN_SCORE) * 100


def _calculate_z_score(raw_mean: float) -> float:
    return (raw_mean - 50) / 10


def compute_trait_displays(trait_sums: dict[str, int]) -> list[TraitDisplay]:
    """Return display metrics for each Big Five trait."""

    raw_means = {
        trait: _scale_to_percentage(total)
        for trait, total in trait_sums.items()
    }
    z_scores = {trait: _calculate_z_score(value) for trait, value in raw_means.items()}

    values = list(z_scores.values())
    mean_z = sum(values) / len(values)
    range_z = max(values) - min(values)

    def boost(z_value: float) -> float:
        if range_z < RANGE_THRESHOLD:
            return (z_value - mean_z) * BOOST_FACTOR + mean_z
        return z_value

    displays: list[TraitDisplay] = []
    for trait in TRAIT_ORDER:
        raw_mean = round(raw_means[trait], RAW_MEAN_DECIMALS)
        z_value = z_scores[trait]
        z_boosted = boost(z_value)
        display = round(max(0, min(100, 50 + z_boosted * DISPLAY_SCALE)))
        displays.append(
            TraitDisplay(
                trait=trait,
                label=TRAIT_LABELS[trait],
                sum_score=trait_sums[trait],
                raw_mean=raw_mean,
                z_score=round(z_value, Z_DECIMALS),
                z_boosted=round(z_boosted, Z_DECIMALS),
                display_score=display,
            )
        )
    return displays


def _to_card(display: TraitDisplay) -> HighlightCard:
    return HighlightCard(
        trait=display.trait,
        label=display.label,
        display_score=display.display_score,
    )


def compute_highlights(displays: Iterable[TraitDisplay]) -> Highlights:
    """Select highlight cards from computed trait displays."""

    items = list(displays)
    strength = max(
        items,
        key=lambda item: (
            item.display_score,
            item.z_boosted,
            item.raw_mean,
        ),
    )
    caution = min(
        items,
        key=lambda item: (
            item.display_score,
            item.z_boosted,
            item.raw_mean,
        ),
    )

    strong_candidates = [
        _to_card(item)
        for item in sorted(
            (x for x in items if x.trait != strength.trait and x.display_score >= 60),
            key=lambda item: item.display_score,
            reverse=True,
        )
    ][:2]

    weak_candidates = [
        _to_card(item)
        for item in sorted(
            (x for x in items if x.trait != caution.trait and x.display_score <= 40),
            key=lambda item: item.display_score,
        )
    ][:2]

    return Highlights(
        signature_strength=_to_card(strength),
        signature_caution=_to_card(caution),
        strong_candidates=tuple(strong_candidates),
        weak_candidates=tuple(weak_candidates),
    )


def serialize_trait_displays(trait_sums: dict[str, int]) -> tuple[list[dict[str, object]], Highlights]:
    """Convenience helper returning trait rows and highlight cards."""

    displays = compute_trait_displays(trait_sums)
    highlights = compute_highlights(displays)
    return [
        {
            "trait": item.trait,
            "label": item.label,
            "sum": item.sum_score,
            "scaled": item.display_score,
            "raw_mean": item.raw_mean,
            "z": item.z_score,
            "z_boosted": item.z_boosted,
            "display_score": item.display_score,
        }
        for item in displays
    ], highlights

def serialize_highlights(highlights: Highlights) -> dict[str, object]:
    return {
        "signature_strength": asdict(highlights.signature_strength),
        "signature_caution": asdict(highlights.signature_caution),
        "strong_candidates": [asdict(card) for card in highlights.strong_candidates],
        "weak_candidates": [asdict(card) for card in highlights.weak_candidates],
        "contrast_summary_locked": highlights.contrast_summary_locked,
    }
