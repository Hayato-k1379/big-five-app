from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0002_rename_analytics_e_event_t_0a8e64_idx_analytics_e_event_t_b30595_idx"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageView",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("path", models.CharField(max_length=255)),
                ("method", models.CharField(max_length=8)),
                ("status_code", models.PositiveSmallIntegerField()),
                ("referrer", models.CharField(blank=True, max_length=255, null=True)),
                ("user_agent", models.TextField(blank=True, null=True)),
                ("ip_hash", models.CharField(blank=True, max_length=64, null=True)),
                ("session_id", models.CharField(blank=True, max_length=64, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="pageview",
            index=models.Index(fields=["created_at"], name="analytics_page_creat_9329d9_idx"),
        ),
        migrations.AddIndex(
            model_name="pageview",
            index=models.Index(fields=["path", "created_at"], name="analytics_page_path_c2b988_idx"),
        ),
    ]
