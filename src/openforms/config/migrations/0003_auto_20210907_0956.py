# Generated by Django 2.2.24 on 2021-09-07 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0002_make_react_ui_default"),
    ]

    operations = [
        migrations.AlterField(
            model_name="globalconfiguration",
            name="enable_react_form",
            field=models.BooleanField(
                default=True,
                help_text="If enabled, the admin page to create forms will use the new React page.",
                verbose_name="enable React form page",
            ),
        ),
    ]
