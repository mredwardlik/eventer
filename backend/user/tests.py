from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from user.models import EditorSetting, User

API = '/api/v1/user/'
PASSWORD = 'a-good-long-password'


class UserTests(APITestCase):
    def register(self, username='anna', email='anna@example.com', password=PASSWORD):
        return self.client.post(API + 'register', {'username': username, 'email': email, 'password': password})

    def login(self, username='anna', password=PASSWORD):
        return self.client.post(API + 'login', {'username': username, 'password': password})

    def test_register_and_login(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('password', response.data)
        self.assertTrue(EditorSetting.objects.filter(user__username='anna').exists())
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['token'], Token.objects.get(user__username='anna').key)
        self.assertEqual(self.login().data['token'], response.data['token'])  # the same token next time

    def test_register_checks_input(self):
        self.register()
        self.assertEqual(self.register().status_code, 400)                                     # taken
        self.assertIn('password', self.register('bob', 'bob@example.com', '123').data)          # weak
        self.assertIn('password', self.register('bobbymarley', 'b@example.com', 'bobbymarley1').data)  # like the name
        self.assertIn('email', self.register('carl', 'not-an-email').data)

    def test_wrong_password(self):
        self.register()
        response = self.login(password='wrong')
        self.assertEqual(response.status_code, 400)
        self.assertIn('not found', str(response.data))

    def test_me_and_logout(self):
        self.register()
        token = self.login().data['token']
        self.assertEqual(self.client.get(API + 'me').status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        me = self.client.get(API + 'me').data
        self.assertEqual(me['username'], 'anna')
        self.assertEqual(set(me), {'id', 'username', 'email', 'first_name', 'last_name', 'last_login'})
        self.assertEqual(self.client.post(API + 'logout').status_code, 204)
        self.assertEqual(self.client.get(API + 'me').status_code, 401)

    def test_editor_setting(self):
        user = User.objects.create_user('anna', password=PASSWORD)
        self.client.force_authenticate(user)
        self.assertEqual(self.client.get(API + 'editor').data, {})  # created on the first request
        value = {'blocks': [{'type': 'paragraph', 'data': {'text': 'Hi'}}]}
        self.assertEqual(self.client.post(API + 'editor', {'value': value}, format='json').status_code, 200)
        self.assertEqual(self.client.get(API + 'editor').data, value)
        self.assertEqual(self.client.post(API + 'editor', {'value': [1]}, format='json').status_code, 400)

    def test_old_debug_endpoints_are_gone(self):
        for path in ('all', 'update', 'identify/abc'):
            self.assertEqual(self.client.get(API + path).status_code, 404)
