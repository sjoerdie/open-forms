# Generated by Django 2.2.24 on 2021-08-20 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stuf', '0006_auto_20210722_1832'),
    ]

    operations = [
        migrations.CreateModel(
            name='JccConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='stuf.SoapService')),
            ],
            options={
                'verbose_name': 'JCC configuration',
            },
        ),
    ]
