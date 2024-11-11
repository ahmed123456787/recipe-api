"""
Test Ingredient API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

from rest_framework import status
from rest_framework.test import APIClient

INGREDIENT_URL=reverse("recipe:ingredient-list")


def detail_url(ingr_id):
    return reverse("recipe:ingredient-detail",args=[ingr_id])


def create_user(email="user@example.com", password="pass123"):
    """create and return user"""
    return get_user_model().objects.create(email=email, password=password)


class PublicIngredientTests (TestCase):
    """Test unathenticated ingredient requests"""
    
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        
    def test_auth_requireda(self):
        """Test auth is required to retreive ingredients"""
        res = self.client.get(INGREDIENT_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateIngredientsTests(TestCase):
    """Test authenticated API requests"""
    
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        
    def test_retreive_ingredients(self):
        """Test retreiving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name="Potatoes")    
        Ingredient.objects.create(user=self.user, name="Tomatoes")    
        
        res = self.client.get(INGREDIENT_URL)
        
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        
                
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data,res.data)
        
        
    def test_ingredients_limited_to_user(self):
        """Test list of ingredients"""
        user_2 = create_user(email="user@gmail.com", password="pass123")
        Ingredient.objects.create(
            user=user_2
            ,name="Potatoes"
        )  
        ingredient = Ingredient.objects.create(user=self.user,name="tomatoes")
        
        res = self.client.get(INGREDIENT_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredient.name)
        self.assertEqual(res.data[0]['id'],ingredient.id)
        
    def test_update_ingredients(self):
        """Test updating an ingredient,  """  
        ingredient = Ingredient.objects.create(user=self.user,name="Tomatoes")
        payload = {
            "name": "vegetables"
        }
        
        url = detail_url(ingredient.id)
        res = self.client.patch(url , payload)
        
        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name,payload["name"])
    
    def test_delete_ingredients(self):
        """Test deleting an ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name="apple")
        
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.all()
        self.assertFalse(ingredients.exists())  