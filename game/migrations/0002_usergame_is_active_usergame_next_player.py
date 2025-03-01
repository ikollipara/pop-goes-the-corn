# Generated by Django 5.1.6 on 2025-03-01 19:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergame',
            name='is_active',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usergame',
            name='next_player',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.DO_NOTHING, related_name='prev_player', to='game.usergame'),
            preserve_default=False,
        ),
    ]
