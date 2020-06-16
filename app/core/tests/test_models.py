from unittest.mock import patch
import uuid

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Tag, Ingredient, \
                        Recipe, create_image_unique_name


def create_user_model(**kwargs):

    payload = {
        'email': 'testcasemail@gmail.com',
        'password': 'testpassword1',
        'name': 'Lora Palmer',
    }

    payload.update(**kwargs)

    return get_user_model().objects.create_user(**payload)


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

        user = create_user_model(
            email=email,
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
        user = create_user_model()
        data = {'owner': user, 'name': 'New Tag'}

        tag = Tag.objects.create(**data)

        self.assertIn(tag, Tag.objects.all())
        self.assertEqual(tag, Tag.objects.get(**data))
        self.assertEqual(data['name'], str(tag))

    def test_ingredient_created(self):
        '''
        Tests if the ingredient has been created and has
        a valid string representation
        '''
        user = create_user_model()

        data = {'owner': user, 'name': 'Cabbage'}
        ingredient = Ingredient.objects.create(**data)

        self.assertIn(ingredient, Ingredient.objects.all())
        self.assertEqual(
            ingredient, Ingredient.objects.get(**data)
        )
        self.assertEqual(data['name'], str(ingredient))

    def test_recipe_model(self):
        '''
        Tests if the recipe model is created and has a valid string
        representation
        '''
        user = create_user_model()

        recipe = Recipe.objects.create(
            owner=user,
            title='New Recipe',
            price=5,
        )

        self.assertIn(recipe, Recipe.objects.all())
        self.assertEqual(str(recipe), 'New Recipe')

    @patch('uuid.uuid4')
    def test_image_upload(self, mock_uuid):
        '''Tests if the image uploaded has a custom unique name'''
        return_uuid = 'test_image'
        mock_uuid.return_value = return_uuid
        back_value = create_image_unique_name(None, 'image.jpg')
        expected_value = f'uploaded/recipe/{return_uuid}.jpg'

        self.assertEqual(back_value, expected_value)
