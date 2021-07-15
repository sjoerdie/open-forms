# Generated by Django 2.2.20 on 2021-07-09 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0024_auto_20210624_1029"),
    ]

    operations = [
        migrations.AddField(
            model_name="form",
            name="begin_text",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed at the start of the form to indicate the user can begin to fill in the form. Leave blank to get value from global configuration.",
                max_length=50,
                verbose_name="begin text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="change_text",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to change a certain step. Leave blank to get value from global configuration.",
                max_length=50,
                verbose_name="change text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="confirm_text",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to confirm the form is filled in correctly. Leave blank to get value from global configuration.",
                max_length=50,
                verbose_name="confirm text",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="previous_text",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the overview page to go to the previous step. Leave blank to get value from global configuration.",
                max_length=50,
                verbose_name="previous text",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="next_text",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to go to the next step. Leave blank to get value from global configuration.",
                max_length=50,
                verbose_name="next text",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="previous_text",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to go to the previous step. Leave blank to get value from global configuration.",
                max_length=50,
                verbose_name="previous text",
            ),
        ),
        migrations.AddField(
            model_name="formstep",
            name="save_text",
            field=models.CharField(
                blank=True,
                help_text="The text that will be displayed in the form step to save the current information. Leave blank to get value from global configuration.",
                max_length=50,
                verbose_name="save text",
            ),
        ),
    ]
