# Generated by Django 3.0.4 on 2020-03-08 05:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20200307_0437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='screen',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Screen'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='showtime',
            field=models.TimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='screen',
            name='seats',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Movie'),
        ),
    ]