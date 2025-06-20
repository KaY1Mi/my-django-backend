# Generated by Django 5.2.1 on 2025-06-07 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='default_avatar',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]
