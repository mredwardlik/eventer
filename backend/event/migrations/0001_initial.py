# Generated by Django 4.0.2 on 2022-05-23 17:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import event.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(error_messages={'unique': 'The event with name you wrote is already created.'}, max_length=100, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=event.models.get_upload_path)),
                ('start_date', models.DateTimeField(null=True)),
                ('end_date', models.DateTimeField(null=True)),
                ('description', models.JSONField(default=event.models.empty_list)),
                ('tags', models.JSONField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('watched', models.IntegerField(default=0)),
                ('liked', models.JSONField(default=event.models.empty_list)),
                ('active', models.BooleanField(default=False)),
                ('user', models.ForeignKey(db_column='username', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
        migrations.CreateModel(
            name='DescriptionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to=event.models.get_upload_path)),
                ('user', models.ForeignKey(db_column='username', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
    ]
