# Generated by Django 5.1.3 on 2024-12-04 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
        migrations.AddField(
            model_name='message',
            name='username',
            field=models.CharField(default='Anonymous', max_length=255),
            preserve_default=False,
        ),
    ]
