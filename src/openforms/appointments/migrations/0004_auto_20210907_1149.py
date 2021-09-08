# Generated by Django 2.2.24 on 2021-09-07 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appointments", "0003_appointmentinfo_start_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointmentinfo",
            name="status",
            field=models.CharField(
                choices=[
                    ("success", "Success"),
                    (
                        "missing_info",
                        "Submission does not contain all the info needed to make an appointment",
                    ),
                    ("failed", "Failed"),
                    ("cancelled", "Cancelled"),
                ],
                max_length=50,
                verbose_name="status",
            ),
        ),
    ]
