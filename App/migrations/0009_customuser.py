# Generated by Django 5.0 on 2024-01-16 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0008_likes_bookmarked'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True)),
            ],
        ),
    ]