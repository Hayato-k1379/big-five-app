from django.db import models


class EventLog(models.Model):
    EVENT_TYPES = [
        ("cta_click", "CTA Click (to note)"),
        ("purchase_note", "Purchase (Note) - inferred"),
    ]

    event_type = models.CharField(max_length=32, choices=EVENT_TYPES)
    session_id = models.CharField(max_length=64, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    referrer = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    extra_payload = models.JSONField(blank=True, null=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["event_type", "occurred_at"])]

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.occurred_at:%Y-%m-%d %H:%M:%S}"


class PageView(models.Model):
    """Stores landing page views for SSR側のLP計測."""

    path = models.CharField(max_length=255)
    method = models.CharField(max_length=8)
    status_code = models.PositiveSmallIntegerField()
    referrer = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    ip_hash = models.CharField(max_length=64, blank=True, null=True)
    session_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["path", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.path} @ {self.created_at:%Y-%m-%d %H:%M:%S}"
