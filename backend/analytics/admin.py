from datetime import timedelta

from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import EventLog, PageView


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "occurred_at", "session_id", "referrer")
    list_filter = ("event_type", "occurred_at")
    search_fields = ("session_id", "referrer", "user_agent")
    date_hierarchy = "occurred_at"


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("created_at", "path", "status_code", "session_id", "ip_hash")
    list_filter = ("path", "status_code", "created_at")
    search_fields = ("referrer", "user_agent", "ip_hash", "session_id")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    change_list_template = "admin/analytics/pageview/change_list.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            cl = response.context_data["cl"]
            queryset = cl.queryset
        except (KeyError, AttributeError):
            return response

        chart_context = self._chart_data(queryset)
        response.context_data.update(chart_context)
        return response

    def _chart_data(self, qs):
        now = timezone.now()
        start = now - timedelta(days=29)
        daily = (
            qs.filter(created_at__gte=start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .order_by("day")
            .annotate(pv=Count("id"), uu=Count("ip_hash", distinct=True))
        )
        labels = [row["day"].strftime("%m/%d") if row["day"] else "" for row in daily]
        pv = [row["pv"] for row in daily]
        uu = [row["uu"] for row in daily]

        last_24h = qs.filter(created_at__gte=now - timedelta(hours=24))
        return {
            "chart_payload": {"labels": labels, "pv": pv, "uu": uu},
            "chart_labels": labels,
            "chart_pv": pv,
            "chart_uu": uu,
            "summary_pv_24h": last_24h.count(),
            "summary_uu_24h": last_24h.values_list("ip_hash", flat=True).distinct().count(),
        }
