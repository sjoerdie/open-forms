# Generated by Django 2.2.20 on 2021-06-24 18:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stuf_zds", "0003_auto_20210604_1355"),
    ]

    operations = [
        migrations.AddField(
            model_name="stufzdsconfig",
            name="zds_documenttype_omschrijving",
            field=models.CharField(
                default="Aanvraag",
                help_text="Documenttype description for newly created zaken in StUF-ZDS",
                max_length=80,
                verbose_name="Documenttype description",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="stufzdsconfig",
            name="zds_zaaktype_status_code",
            field=models.CharField(
                default="ONTV",
                help_text="Zaaktype status code for newly created zaken in StUF-ZDS",
                max_length=10,
                verbose_name="Zaaktype status code",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="stufzdsconfig",
            name="gemeentecode",
            field=models.CharField(
                help_text="Municipality code to register zaken",
                max_length=4,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Expected a numerical value.", regex="^[0-9]+$"
                    )
                ],
                verbose_name="Municipality code",
            ),
        ),
        migrations.AlterField(
            model_name="stufzdsconfig",
            name="zds_zaaktype_code",
            field=models.CharField(
                help_text="Zaaktype code for newly created zaken in StUF-ZDS",
                max_length=10,
                verbose_name="Zaaktype code",
            ),
        ),
        migrations.AlterField(
            model_name="stufzdsconfig",
            name="zds_zaaktype_omschrijving",
            field=models.CharField(
                help_text="Zaaktype description for newly created zaken in StUF-ZDS",
                max_length=80,
                verbose_name="Zaaktype description",
            ),
        ),
    ]
