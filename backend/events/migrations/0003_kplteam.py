import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0002_event_match_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="KPLTeam",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("short_name", models.CharField(blank=True, help_text="e.g. GOR, AFC", max_length=20)),
                ("logo_url", models.URLField(blank=True, help_text="TheSportsDB badge URL")),
                ("primary_color", models.CharField(default="#000000", help_text="Hex color", max_length=7)),
                ("secondary_color", models.CharField(default="#FFFFFF", help_text="Hex color", max_length=7)),
                ("home_stadium", models.CharField(blank=True, max_length=200)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("founded", models.PositiveIntegerField(blank=True, null=True)),
                ("thesportsdb_id", models.CharField(blank=True, db_index=True, max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "KPL Team",
                "verbose_name_plural": "KPL Teams",
                "ordering": ["name"],
            },
        ),
    ]
