from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from rest_framework import status
from rest_framework.test import APIClient

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
