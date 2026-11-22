from django.db import migrations, models

import event.models


def fill_empty_cities(apps, schema_editor):
    Event = apps.get_model('event', 'Event')
    Event.objects.filter(city__isnull=True).update(city='Almaty')


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(fill_empty_cities, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='event',
            name='city',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.JSONField(default=event.models.empty_document),
        ),
    ]
