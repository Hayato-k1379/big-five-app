from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EventLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("cta_click", "CTA Click (to note)"),
                            ("purchase_note", "Purchase (Note) - inferred"),
                        ],
                        max_length=32,
                    ),
                ),
                ("session_id", models.CharField(blank=True, max_length=64, null=True)),
                ("user_id", models.IntegerField(blank=True, null=True)),
                ("referrer", models.CharField(blank=True, max_length=255, null=True)),
                ("user_agent", models.TextField(blank=True, null=True)),
                ("extra_payload", models.JSONField(blank=True, null=True)),
                ("occurred_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["event_type", "occurred_at"], name="analytics_e_event_t_0a8e64_idx")
                ],
            },
        ),
    ]
