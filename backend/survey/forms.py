"""Forms for the Big Five survey."""
from __future__ import annotations

from typing import Iterable

from django import forms

from .models import PersonalityItem

LIKERT_CHOICES = [
    ("1", "まったく当てはまらない"),
    ("2", "あまり当てはまらない"),
    ("3", "どちらともいえない"),
    ("4", "まあ当てはまる"),
    ("5", "とても当てはまる"),
]


class SurveyForm(forms.Form):
    """Dynamic form that renders one field per personality item."""

    def __init__(self, *, items: Iterable[PersonalityItem], **kwargs) -> None:
        self.items = list(items)
        super().__init__(**kwargs)
        for item in self.items:
            field_name = item.code
            self.fields[field_name] = forms.ChoiceField(
                choices=LIKERT_CHOICES,
                widget=forms.RadioSelect,
                label=item.text_ja,
                required=True,
            )
            self.fields[field_name].widget.attrs.update({"class": "form-check-input"})
