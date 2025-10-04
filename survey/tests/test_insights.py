"""Unit tests for the scoring insights helpers."""
from __future__ import annotations

from django.test import SimpleTestCase

from survey.constants import TRAIT_ORDER
from survey.insights import compute_highlights, compute_trait_displays


class InsightComputationTests(SimpleTestCase):
    def test_boost_applies_when_trait_range_is_small(self) -> None:
        trait_sums = {trait: total for trait, total in zip(TRAIT_ORDER, [32, 31, 30, 29, 29])}
        displays = compute_trait_displays(trait_sums)
        boosted_diffs = [item.z_boosted - item.z_score for item in displays]
        self.assertTrue(any(abs(diff) > 1e-9 for diff in boosted_diffs))

        highlights = compute_highlights(displays)
        self.assertEqual(highlights.signature_strength.trait, "O")
        self.assertEqual(highlights.signature_caution.trait, "A")

    def test_no_boost_when_trait_range_is_large(self) -> None:
        trait_sums = {trait: total for trait, total in zip(TRAIT_ORDER, [50, 45, 40, 35, 30])}
        displays = compute_trait_displays(trait_sums)
        self.assertTrue(all(abs(item.z_boosted - item.z_score) < 1e-9 for item in displays))

        highlights = compute_highlights(displays)
        self.assertEqual(highlights.signature_strength.trait, "O")
        self.assertEqual(highlights.signature_caution.trait, "N")
        strong_traits = {card.trait for card in highlights.strong_candidates}
        self.assertIn("C", strong_traits)
