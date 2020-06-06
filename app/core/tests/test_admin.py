from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminTest(TestCase):

    def setUp(self):
        '''Setting up the user, superuser and test Client'''
        self.client = Client()

        self.user = get_user_model().objects.create_user(
            email='testmail@gmail.com',
            name='kiriki',
            password='testpassword',
        )

        self.superuser = get_user_model().objects.create_superuser(
            email='testmail2@gmail.com',
            name='kirirki',
            password='testpassword'
        )
        self.client.force_login(self.superuser)

    def test_user_listed(self):
        '''
        Testing, if user name and email is listed
        on the admin site
        '''
        url = reverse('admin:core_user_changelist')

        self.assertContains(self.client.get(url), self.user.name)
        self.assertContains(self.client.get(url), self.user.email)

    def test_user_change_page(self):
        '''Tests if the page can be opened'''
        url = reverse('admin:core_user_change', args=[self.user.id])

        self.assertEqual(self.client.get(url).status_code, 200)

    def test_user_create_page(self):
        '''Tests if the user add page can be opened'''
        url = reverse('admin:core_user_add')

        self.assertEqual(self.client.get(url).status_code, 200)
