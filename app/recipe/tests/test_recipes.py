import tempfile
import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from rest_framework import status
from rest_framework.test import APIClient

from PIL import Image

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipes-list')


def create_user_model(**kwargs):

    payload = {
        'email': 'testmail@gmail.com',
        'password': 'testpassword',
        'name': 'testname',
    }
    payload.update(kwargs)

    return get_user_model().objects.create_user(**payload)


def create_recipe(user, **kwargs):

    payload = {
        'title': 'Test',
        'price': 5.00,
        'owner': user,
    }
    payload.update(kwargs)

    return Recipe.objects.create(**payload)


def create_tag(name, user):
    return Tag.objects.create(name=name, owner=user)


def create_ingredient(name, user):
    return Ingredient.objects.create(name=name, owner=user)


def create_detail_link(pk):
    return reverse('recipe:recipes-detail', args=[pk])


def create_upload_link(pk):
    return reverse('recipe:recipes-upload-image', args=[pk])


class PublicInteraction(TestCase):
    '''Tests all anonyous users interactions with recipes'''

    def setUp(self):
        self.client = APIClient()

    def test_cant_view_recipes(self):
        '''Tests if anonymous user can view the list of recipes'''
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cant_create_recipes(self):
        '''Tests if anonymous user can create a new recipe'''
        payload = {
            'title': 'kebab',
            'price': 5.00,
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInteraction(TestCase):
    '''Tests all authorized user interactions with the api'''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user_model()
        self.client.force_authenticate(self.user)

    def test_can_view_recipes(self):
        '''Tests if the user can view his recipes'''
        create_recipe(self.user)
        serializer = RecipeSerializer(
            Recipe.objects.all().filter(owner=self.user).order_by('-id'),
            many=True
        )

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_can_view_own_recipes(self):
        '''Test if user views only his recipes'''
        new_user = create_user_model(email='newMail@gmail.com')

        create_recipe(self.user)
        create_recipe(new_user)

        res = self.client.get(RECIPE_URL)

        self.assertEqual(len(res.data), 1)

    def test_can_create_recipes(self):
        '''Test if user can create recipes'''
        payload = {
            'title': 'New Recipe',
            'price': 5,
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_can_retrieve_detail(self):
        '''Test if user can retrieve the details of the recipe'''
        recipe = create_recipe(self.user)

        recipe.tags.add(create_tag('new_tag', self.user))
        recipe.ingredients.add(create_ingredient('new_ingredient', self.user))
        serializer = RecipeDetailSerializer(recipe)

        res = self.client.get(create_detail_link(recipe.pk))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_can_patch(self):
        '''Tests if the user can partially update the recipe'''
        new_tag = create_tag('new_two', self.user)
        recipe = create_recipe(self.user)

        recipe.tags.add(create_tag('new_tag', self.user))
        recipe.ingredients.add(create_ingredient('new_ingredient', self.user))

        url = create_detail_link(recipe.pk)
        res = self.client.patch(url, {'title': 'Carry', 'tags': [new_tag.pk]})

        recipe.refresh_from_db()
        tags = recipe.tags.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, 'Carry')
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_can_put(self):
        '''Tests if the user can fully update the model'''
        payload = {
            'title': 'Kingy',
            'price': 5.99,
        }

        recipe = create_recipe(self.user)

        recipe.tags.add(create_tag('new_tag', self.user))
        recipe.ingredients.add(create_ingredient('new_ingredient', self.user))

        url = create_detail_link(recipe.pk)
        res = self.client.put(url, payload)
        recipe.refresh_from_db()
        tags = recipe.tags.all()
        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(tags), 0)
        self.assertEqual(len(ingredients), 0)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(float(recipe.price), payload['price'])

    def test_is_filtered_by_tags(self):
        '''
        Tests if the list is filtered by tags when the arguments are
        passed to the request
        '''
        recipe_1 = create_recipe(self.user, title='Test_1')
        recipe_2 = create_recipe(self.user, title='Test_2')
        recipe_3 = create_recipe(self.user, title='Test_3')

        tag_1 = create_tag('Tag_1', self.user,)
        tag_2 = create_tag('Tag_2', self.user)
        serializer = RecipeSerializer([recipe_2, recipe_1], many=True)
        serializer_2 = RecipeSerializer(recipe_3)

        recipe_1.tags.add(tag_1)
        recipe_2.tags.add(tag_2)

        res = self.client.get(RECIPE_URL, {'tags': f'{tag_1.pk}, {tag_2.pk}'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)

    def test_filtered_by_ingredients(self):
        '''
        Tests if recipies are filtered by ingredients if the user passes
        the arguments in the request
        '''
        recipe_1 = create_recipe(self.user, title='Test_1')
        recipe_2 = create_recipe(self.user, title='Test_2')
        recipe_3 = create_recipe(self.user, title='Test_3')

        ingr_1 = create_ingredient('Ingr_1', self.user)
        ingr_2 = create_ingredient('Ingr_2', self.user)
        serializer = RecipeSerializer([recipe_2, recipe_1], many=True)
        serializer_2 = RecipeSerializer(recipe_3)

        recipe_1.ingredients.add(ingr_1)
        recipe_2.ingredients.add(ingr_2)

        res = self.client.get(RECIPE_URL,
                              {'ingredients': f'{ingr_1.pk}, {ingr_2.pk}'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)


class RecipesImagesTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user_model()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_image_successfully_uploaded(self):
        '''Tests if the user can upload a new image to his recipe'''
        url = create_upload_link(self.recipe.pk)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            image = Image.new('RGB', (10, 10))
            image.save(ntf, format='JPEG')
            ntf.seek(0)

            res = self.client.post(url, {'image': ntf}, format='multipart')
            self.recipe.refresh_from_db()

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('image', res.data)
            self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_post_invalid_file(self):
        '''Tests that the request will be bad if the user will post nothing'''
        url = create_upload_link(self.recipe.pk)

        res = self.client.post(url, {'image': ' '}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
