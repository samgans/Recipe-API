from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create_user')

TOKEN_URL = reverse('user:get_token')

PROFILE_URL = reverse('user:view_user')

USER_DATA = {
    'email': 'test_mail@gmail.com',
    'password': 'testpassword',
    'name': 'Battoria',
}


class PublicInteraction(TestCase):
    '''Tests all public requests related to user model'''
    def setUp(self):
        self.client = APIClient()

    def test_user_created(self):
        '''Test checks if the user can be created'''
        res = self.client.post(CREATE_USER_URL, USER_DATA)
        user = get_user_model().objects.get(**res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data.get('email'), USER_DATA['email'].lower())
        self.assertTrue(user.check_password(USER_DATA.get('password')))
        self.assertNotIn('password', res.data)

    def test_user_without_email(self):
        '''Tests if the user can be created without the email'''
        res = self.client.post(
            CREATE_USER_URL,
            {'email': '', 'password': 'testpassword'},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_short_password(self):
        '''Tests if the user can be created with password too short'''
        res = self.client.post(
            CREATE_USER_URL,
            {'email': 'testmail@gmail.com', 'password': 'pw'}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
                                    email=USER_DATA['email']).exists()
        self.assertFalse(user_exists)

    def test_returns_auth_token(self):
        '''Tests if valid request returns token'''
        get_user_model().objects.create_user(**USER_DATA)
        res = self.client.post(TOKEN_URL, USER_DATA)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_token_invalid_pass(self):
        '''Tests if token created with invalid password'''
        get_user_model().objects.create_user(**USER_DATA)
        res = self.client.post(
            TOKEN_URL,
            {
                'email': 'testmail@gmail.com',
                'password': 'invalidpass',
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_without_user(self):
        '''Tests if token created without valid user'''
        res = self.client.post(
            TOKEN_URL,
            {
                'email': 'testmail@gmail.com',
                'password': 'invalidpass',
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_anonimous_user_profile(self):
        '''Tests that non-authorized user can't view account information'''
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInteraction(TestCase):
    '''Tests the authenticated requests to user model'''
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(**USER_DATA)
        self.client.force_authenticate(user=self.user)

    def test_if_updates(self):
        '''Tests if the user profile updates in case data is valid'''
        patcher = {
            'password': 'testpasswordnew',
            'name': 'Tony'
        }
        res = self.client.patch(PROFILE_URL, patcher)

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, patcher['name'])
        self.assertTrue(self.user.check_password(patcher['password']))

    def test_if_can_see(self):
        '''Tests if the authenticated user can see his profile'''
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_not_allowed(self):
        '''Test if post request is not allowed'''
        res = self.client.post(PROFILE_URL, {'hello': 'qq'})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
