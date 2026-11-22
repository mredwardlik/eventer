"""``python manage.py seed``: a demo organizer with a few events, to try the app at once."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from event.models import Event
from user.models import EditorSetting, User

USERNAME = 'demo'
PASSWORD = 'eventer-demo'


def document(*blocks):
    return {'time': 0, 'version': '2.24.3', 'blocks': [{'type': kind, 'data': data} for kind, data in blocks]}


EVENTS = [
    {
        'name': 'Almaty Jazz Night',
        'city': 'Almaty',
        'tags': ['Concert', 'Festival'],
        'days': 12,
        'hours': 4,
        'description': document(
            ('header', {'text': 'An evening of live jazz', 'level': 2}),
            ('paragraph', {'text': 'Three bands, one stage and a view of the mountains. Doors open an hour '
                                   'before the first set.'}),
            ('list', {'style': 'unordered', 'items': ['19:00: doors open', '20:00: the first set',
                                                      '23:00: jam session']}),
        ),
    },
    {
        'name': 'Python for Beginners',
        'city': 'Pavlodar',
        'tags': ['Master Class', 'Training'],
        'days': 5,
        'hours': 3,
        'description': document(
            ('header', {'text': 'Write your first program', 'level': 2}),
            ('paragraph', {'text': 'Bring a laptop. We install Python together and write a small game.'}),
        ),
    },
    {
        'name': 'Spring Book Fair',
        'city': 'Shymkent',
        'tags': ['Fair', 'Presentation'],
        'days': 30,
        'hours': 8,
        'description': document(('paragraph', {'text': 'Publishers, authors and second-hand books.'})),
    },
]


class Command(BaseCommand):
    help = f'Create the user "{USERNAME}" (password "{PASSWORD}") with demo events.'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username=USERNAME, defaults={'email': 'demo@example.com'})
        if created:
            user.set_password(PASSWORD)
            user.save()
        EditorSetting.objects.get_or_create(user=user)
        start = timezone.localtime().replace(hour=19, minute=0, second=0, microsecond=0)
        made = 0
        for data in EVENTS:
            begins = start + timedelta(days=data['days'])
            _, new = Event.objects.get_or_create(name=data['name'], defaults={
                'user': user, 'city': data['city'], 'tags': data['tags'], 'description': data['description'],
                'start_date': begins, 'end_date': begins + timedelta(hours=data['hours']),
            })
            made += new
        self.stdout.write(self.style.SUCCESS(
            f'User "{USERNAME}" with password "{PASSWORD}", {made} new event(s).'))
