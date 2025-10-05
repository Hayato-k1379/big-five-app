from django.contrib import admin

from .models import EventLog


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "occurred_at", "session_id", "referrer")
    list_filter = ("event_type", "occurred_at")
    search_fields = ("session_id", "referrer", "user_agent")
    date_hierarchy = "occurred_at"
