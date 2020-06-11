from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Tag


class ModelTests(TestCase):

    def test_create_user_model_mail(self):
        '''
        Test creates the user model
        and checks if the mail and password created are valid
        '''

        email = 'testcasemail@gmail.com'
        password = 'testpassword1'
        name = 'Lora Palmer'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name,
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.name, name)
        self.assertTrue(user.check_password(password))

    def test_mail_validation(self):
        '''Test validates that mail suffix is made .lower() by python'''

        email = 'testcasemail@GMAIL.cOm'
        password = 'testpassword1'
        name = 'Lora Palmer'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name,
        )

        self.assertEqual(user.email, email.lower())

    def test_validation_without_mail_and_username(self):
        '''
        Test checks if the authorization works without the mail
        and without the name
        '''

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'tony')
            get_user_model().objects.create_user('test@gmail.com', None)
            get_user_model().objects.create_user(None, None)

    def test_superuser_created(self):
        '''Test checks if new superuser has been created'''

        email = 'testcasemail@GMAIL.cOm'
        password = 'testpassword1'
        name = 'Lora Palmer'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            name=name,
        )

        self.assertTrue(
            user in get_user_model().objects.all()
            and user.is_superuser
            and user.is_staff
        )

        def test_tag_created(self):
            '''
            Tests if the tag has been created and has a valid
            string representation
            '''
            user = get_user_model().objects.create_user(
                email=email,
                password=password,
                name=name,
            )

            data = {'owner': user, 'name': 'New Tag'}

            tag = Tag.objects.create(**data)

            self.assertIn(tag, Tag.objects.all())
            self.assertEqual(tag, Tag.objects.get(**data))
            self.assertEqual(data['name'], str(tag))
