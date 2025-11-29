from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="surveyresult",
            name="memo",
            field=models.CharField(
                blank=True,
                default="",
                help_text="20文字程度のメモ",
                max_length=50,
                verbose_name="メモ",
            ),
        ),
    ]
