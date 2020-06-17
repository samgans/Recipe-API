from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tags-list')


def create_recipe(user, **kwargs):

    payload = {
        'title': 'Test',
        'price': 5.00,
        'owner': user,
    }
    payload.update(kwargs)

    return Recipe.objects.create(**payload)


def create_user(email='testmail@gmail.com', password='testpassword',
                name='VitoScaletta'):
    return get_user_model().objects.create_user(email, name, password)


def create_tag(user, name):
    return Tag.objects.create(owner=user, name=name)


class PublicInteraction(TestCase):
    '''Tests all anonymous interactions with the API'''

    def setUp(self):
        self.client = APIClient()

    def test_cant_get_tag(self):
        '''Tests that anonymous user can't view the tags'''
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cant_create_tag(self):
        '''Tests that anonymous user can't create the tag'''
        res = self.client.post(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInteraction(TestCase):
    '''Tests all authorized interactions with the API'''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_if_can_view(self):
        '''Tests if the user can view tags'''
        create_tag(self.user, 'Tag1')
        create_tag(self.user, 'Tag2')
        tags = Tag.objects.all().order_by('-name')

        res = self.client.get(TAG_URL)

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_for_one_user(self):
        '''Tests if user can retrieve only his tags'''
        create_tag(self.user, 'Tag1')
        create_tag(self.user, 'Tag2')
        other_tag = (
            create_user('tony@gmail.com', 'test', 'testpassword'),
            'Tag From Second User'
        )

        res = self.client.get(TAG_URL)
        serializer = TagSerializer(other_tag)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(serializer, res.data)

    def test_if_tag_created(self):
        '''
        Tests if the tag can be created and the data
        in this new tag matches the data of the request
        '''
        res = self.client.post(TAG_URL, {'name': 'Vegan'})
        tag = Tag.objects.all().filter(name='Vegan', owner=self.user)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(tag.exists())
        self.assertEqual('Vegan', str(tag[0]))

    def test_invalid_tag_data(self):
        '''Tests if the tag is created when invalid data provided'''
        res = self.client.post(TAG_URL, {'name': ''})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_filter_tags_by_recepies(self):
        '''Tests if the user can filter tags assigned to recepies'''
        tag_1 = create_tag(self.user, name='One')
        tag_2 = create_tag(self.user, name='Two')
        tag_3 = create_tag(self.user, name='Three')

        recipe = create_recipe(self.user)

        recipe.tags.add(tag_1, tag_2)
        serializer_1 = TagSerializer([tag_2, tag_1], many=True)
        serializer_2 = TagSerializer(tag_3)

        res = self.client.get(TAG_URL, {'assigned': '1'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)

    def test_can_filter_tags_without_recepies(self):
        '''
        Tests if a user can retrieve all tags not assigned to any recepies
        '''
        tag_1 = create_tag(self.user, name='One')
        tag_2 = create_tag(self.user, name='Two')
        tag_3 = create_tag(self.user, name='Three')

        recipe = create_recipe(self.user)

        recipe.tags.add(tag_1, tag_2)
        serializer_1 = TagSerializer([tag_2, tag_1], many=True)
        serializer_2 = TagSerializer(
            [tag_3, ],
            many=True
        )

        res = self.client.get(TAG_URL, {'not_assigned': '1'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_2.data, res.data)
        self.assertNotIn(serializer_1.data, res.data)

    def test_unique_filtering(self):
        '''Tests if tags returned by filters are unique'''
        tag_1 = create_tag(self.user, 'One')

        recipe = create_recipe(self.user)
        recipe_2 = create_recipe(self.user, title='another')

        recipe.tags.add(tag_1)
        recipe_2.tags.add(tag_1)

        res = self.client.get(TAG_URL, {'assigned': '1'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
