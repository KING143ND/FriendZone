# Generated by Django 5.0 on 2024-01-12 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0005_alter_post_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]