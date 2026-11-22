import io
import shutil
import tempfile
from datetime import datetime, timezone

from django.core.management import call_command
from django.test import override_settings
from PIL import Image as PILImage
from rest_framework.test import APITestCase

from event.models import Event, Image
from user.models import User

API = '/api/v1/event/'
MEDIA = tempfile.mkdtemp()


def png(name='cover.png'):
    data = io.BytesIO()
    PILImage.new('RGB', (4, 4), 'red').save(data, 'PNG')
    data.name = name
    data.seek(0)
    return data


@override_settings(MEDIA_ROOT=MEDIA)
class EventTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.owner = User.objects.create_user('owner', password='x-long-password')
        self.guest = User.objects.create_user('guest', password='x-long-password')

    def make(self, **fields):
        data = {'user': self.owner, 'name': 'Jazz', 'city': 'Almaty', 'tags': ['Concert']}
        data.update(fields)
        return Event.objects.create(**data)

    def create(self, **fields):
        data = {'name': 'Jazz Night', 'city': 'Almaty', 'tags': '["Concert", "Festival"]',
                'description': '{"blocks": []}', 'start_date': '1767268800', 'end_date': '1767283200'}
        data.update(fields)
        return self.client.post(API + 'create', {k: v for k, v in data.items() if v is not None},
                                format='multipart')

    # creating

    def test_create_like_the_frontend(self):
        self.client.force_authenticate(self.owner)
        response = self.create(image=png())
        self.assertEqual(response.status_code, 201, response.data)
        event = Event.objects.get(name='Jazz Night')
        self.assertEqual(event.user, self.owner)
        self.assertEqual(event.tags, ['Concert', 'Festival'])
        self.assertEqual(event.start_date, datetime(2026, 1, 1, 12, tzinfo=timezone.utc))
        self.assertTrue(event.image.name.startswith(f'{self.owner.id}/'))

    def test_create_needs_a_login(self):
        self.assertEqual(self.create().status_code, 401)
        self.assertFalse(Event.objects.exists())

    def test_create_validation(self):
        self.client.force_authenticate(self.owner)
        cases = {
            'tags': {'tags': '["Rave"]'},
            'city': {'city': 'Paris'},
            'end_date': {'end_date': '1767200000'},  # before the start
            'description': {'description': '[1, 2]'},
            'image': {'image': io.BytesIO(b'not an image')},
        }
        for field, data in cases.items():
            with self.subTest(field):
                response = self.create(**data)
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertIn('tags', self.create(tags='[]').data)

    def test_counters_cannot_be_set_by_the_client(self):
        self.client.force_authenticate(self.owner)
        self.create(watched='1000', registered='[{"email": "fake@example.com"}]', user='guest')
        event = Event.objects.get()
        self.assertEqual((event.watched, event.registered, event.user), (0, [], self.owner))

    # reading

    def test_public_event_hides_guests(self):
        event = self.make(registered=[{'name': 'A', 'email': 'a@example.com', 'contacts': '+7'}])
        data = self.client.get(API + 'get', {'id': str(event.id)}).data
        self.assertNotIn('registered', data)
        self.assertEqual(data['user'], 'owner')
        self.assertEqual(data['watched'], 1)
        for item in self.client.get(API + 'all').data:
            self.assertNotIn('registered', item)

    def test_every_view_is_counted(self):
        event = self.make()
        for _ in range(3):
            self.client.get(API + 'get', {'id': str(event.id)})
        event.refresh_from_db()
        self.assertEqual(event.watched, 3)

    def test_missing_events(self):
        hidden = self.make(active=False)
        for query in ({}, {'id': 'nonsense'}, {'id': '00000000-0000-0000-0000-000000000000'},
                      {'id': str(hidden.id)}):
            self.assertEqual(self.client.get(API + 'get', query).status_code, 404)
        self.assertEqual(self.client.get(API + 'all').data, [])

    def test_owner_sees_own_events_with_guests(self):
        mine = self.make(registered=[{'name': 'A', 'email': 'a@example.com', 'contacts': '+7'}])
        self.make(name='Other', user=self.guest)
        self.make(name='Hidden', active=False)
        self.client.force_authenticate(self.owner)
        data = self.client.get(API + 'user').data
        self.assertEqual([item['id'] for item in data], [str(mine.id)])
        self.assertEqual(data[0]['registered'][0]['email'], 'a@example.com')
        self.assertNotIn('password', str(data))

    # guests

    def test_register_for_an_event(self):
        event = self.make()
        guest = {'name': 'Anna', 'email': 'anna@example.com', 'contacts': '@anna'}
        self.assertEqual(self.client.patch(API + f'register/{event.id}', guest).status_code, 200)
        again = self.client.patch(API + f'register/{event.id}', {**guest, 'email': 'ANNA@example.com'})
        self.assertEqual(again.status_code, 400)
        self.assertEqual(self.client.patch(API + f'register/{event.id}', {'name': 'x'}).status_code, 400)
        event.refresh_from_db()
        self.assertEqual(event.registered, [guest])

    def test_cannot_register_for_a_hidden_event(self):
        event = self.make(active=False)
        response = self.client.patch(API + f'register/{event.id}', {'name': 'A', 'email': 'a@b.kz', 'contacts': '1'})
        self.assertEqual(response.status_code, 404)

    def test_like(self):
        event = self.make()
        self.client.force_authenticate(self.guest)
        self.assertEqual(self.client.patch(API + f'like/{event.id}').data['likes'], 1)
        self.assertEqual(self.client.patch(API + f'like/{event.id}').status_code, 403)  # twice
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.patch(API + f'like/{event.id}').status_code, 403)  # own event

    def test_delete_hides_only_own_events(self):
        event = self.make()
        self.client.force_authenticate(self.guest)
        self.assertEqual(self.client.delete(API + f'delete/{event.id}').status_code, 404)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(API + f'delete/{event.id}').status_code, 200)
        event.refresh_from_db()
        self.assertFalse(event.active)

    # images and lists

    def test_editor_image_upload(self):
        self.assertEqual(self.client.post(API + 'image', {'image': png()}, format='multipart').status_code, 401)
        self.client.force_authenticate(self.owner)
        response = self.client.post(API + 'image', {'image': png()}, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['success'], 1)
        self.assertTrue(response.data['file']['url'].startswith('http://testserver/media/'))
        self.assertEqual(Image.objects.get().user, self.owner)
        bad = self.client.post(API + 'image', {'image': io.BytesIO(b'text')}, format='multipart')
        self.assertEqual((bad.status_code, bad.data['success']), (400, 0))

    def test_cities_and_tags(self):
        self.assertIn('Almaty', self.client.get(API + 'special/cities').data)
        self.assertIn('Concert', self.client.get(API + 'special/tags').data)
        self.assertEqual(self.client.get(API + 'special/other').status_code, 404)

    def test_seed(self):
        call_command('seed', stdout=io.StringIO())
        call_command('seed', stdout=io.StringIO())  # twice is fine
        self.assertEqual(Event.objects.filter(user__username='demo').count(), 3)
        self.assertTrue(self.client.login(username='demo', password='eventer-demo'))
