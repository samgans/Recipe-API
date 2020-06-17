from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredients-list')


def create_recipe(user, **kwargs):

    payload = {
        'title': 'Test',
        'price': 5.00,
        'owner': user,
    }
    payload.update(kwargs)

    return Recipe.objects.create(**payload)


def create_new_user(email, name, password):
    return get_user_model().objects.create_user(email, name, password)


def create_ingredient(owner, name):
    return Ingredient.objects.create(owner=owner, name=name)


class PublicInteraction(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_anonymous_cant_view(self):
        '''Tests that anonymous user can't view the list of ingredients'''
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_cant_create(self):
        '''Tests that anonymous user can't create a new ingredient'''
        res = self.client.post(INGREDIENT_URL, {'name': 'Cabbage'})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInteraction(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_new_user(
            'testmail@gmail.com',
            'user',
            'testpassword',
        )
        self.client.force_authenticate(self.user)

    def test_if_can_view(self):
        '''Tests if the user can view his ingredients'''
        create_ingredient(self.user, 'cabbage')
        ingredient = Ingredient.objects.filter(name='cabbage',
                                               owner=self.user)

        res = self.client.get(INGREDIENT_URL)

        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_limited_for_one_user(self):
        '''Tests if the user can see only his ingredients'''
        user_2 = create_new_user(
            'another@gmail.com',
            'test2',
            'testpassword'
        )

        create_ingredient(user_2, 'Pickle')
        create_ingredient(self.user, 'Cabbage')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_can_create_ingredient(self):
        '''Tests that the user can create new ingredient'''
        res = self.client.post(INGREDIENT_URL, {'name': 'Cabbage'})
        ingredient = Ingredient.objects.filter(name='Cabbage',
                                               owner=self.user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ingredient.exists())
        self.assertEqual(str(ingredient[0]), 'Cabbage')

    def test_cant_create_ingredient(self):
        '''
        Tests that if the user provides invalid data, ingredient will not be
        created
        '''
        res = self.client.post(INGREDIENT_URL, {'name': ''})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_filter_ingredients_by_recipe(self):
        '''
        Tests if the user can retrieve the ingredients assigned to recepies
        '''
        ingredient_1 = create_ingredient(self.user, 'One')
        ingredient_2 = create_ingredient(self.user, 'Two')
        ingredient_3 = create_ingredient(self.user, 'Three')

        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient_1, ingredient_2)
        serializer_1 = IngredientSerializer(
            [ingredient_2, ingredient_1],
            many=True
        )
        serializer_2 = IngredientSerializer(ingredient_3)

        res = self.client.get(INGREDIENT_URL, {'assigned': '1'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)

    def test_can_filter_ingrs_without_recipe(self):
        '''
        Tests if the user can retrieve ingredients which are not assigned
        to any recepies
        '''
        ingredient_1 = create_ingredient(self.user, 'One')
        ingredient_2 = create_ingredient(self.user, 'Two')
        ingredient_3 = create_ingredient(self.user, 'Three')

        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient_1, ingredient_2)
        serializer_1 = IngredientSerializer(
            [ingredient_2, ingredient_1],
            many=True
        )
        serializer_2 = IngredientSerializer(
            [ingredient_3, ],
            many=True
        )

        res = self.client.get(INGREDIENT_URL, {'not_assigned': '1'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_2.data, res.data)
        self.assertNotIn(serializer_1.data, res.data)

    def test_unique_filtering(self):
        '''Tests if the ingredients returned by filters are unique'''
        ingredient_1 = create_ingredient(self.user, 'One')

        recipe = create_recipe(self.user)
        recipe_2 = create_recipe(self.user, title='another')

        recipe.ingredients.add(ingredient_1)
        recipe_2.ingredients.add(ingredient_1)

        res = self.client.get(INGREDIENT_URL, {'assigned': '1'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
