import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                help_text="Kenyan phone number: 07XXXXXXXX, 01XXXXXXXX, or 254XXXXXXXXX",
                max_length=13,
                null=True,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Enter a valid Kenyan phone number: 07XXXXXXXX, 01XXXXXXXX, or 254XXXXXXXXX",
                        regex="^(254[0-9]{9}|0[71][0-9]{8})$",
                    )
                ],
            ),
        ),
    ]
