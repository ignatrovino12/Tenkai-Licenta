# Generated by Django 5.0.3 on 2024-06-08 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpx_app', '0004_comment_upvote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='city',
            field=models.CharField(default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='video',
            name='country',
            field=models.CharField(default='Unknown', max_length=50),
        ),
    ]