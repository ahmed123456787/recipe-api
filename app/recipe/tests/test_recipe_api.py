"""
Test for recipe API
"""

from decimal import Decimal
import tempfile
import os
from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    IngredientSerializer
)
RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return a single recipe detail URL"""
    return reverse("recipe:recipe-detail", args=[recipe_id])

def image_upload_url(recipe_id):
    """Create and return an image upload url"""
    return reverse("recipe:recipe-upload-image",args=[recipe_id])



def create_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal("23.34"),
        'link': "http://def.com",
        'description': 'Sample description text'
    }
    
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    return get_user_model().objects.create(**params)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated recipe API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access the API"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated recipe API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user= create_user(email="user@example.com", password="test123")
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by("-id")
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test that recipe list is limited to the authenticated user"""
        other_user = create_user(email="def@gmail.com",password="def123")
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test retrieving a recipe detail"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(instance=recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 22,
            'price': Decimal('23.34'),
            'link': "http://def.com"
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)
        
    def test_partial_update(self):
        """Test update a recipe"""
        original_link = "http://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="smaple test",
            link = original_link
        )
        payload = {"title":"Now recipe"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])    
        self.assertEqual(recipe.link,original_link)    
        self.assertEqual(recipe.user,self.user)    
        
        
    def test_full_update(self):
        """Test full update of a recipe"""
        recipe = create_recipe(
            user=self.user,
            title="def",
            link="https",
            description="defuidf dsjfas",
        )    
        payload = {
            "title":"def",
            "link":"https://def.com",
            "description":"defuidf fds dsjfas",
            "price":Decimal("3.33"),
            "time_minutes":23,
            
        }
        url = detail_url(recipe.id)
        res = self.client.put(url,payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe,k),v)
        
        self.assertEqual(recipe.user,self.user)
    
    
    def test_create_recipe_with_new_tag(self):
        """Test creating a recipe with new tag"""
        payload = {
            "title":"taih recipe",
            "time_minutes":30,
            "price":Decimal("2.50"),
            "tags": [{"name":"tai"},{"name":"Dinner"}]
        }
        res = self.client.post(RECIPES_URL, payload,format="json")
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(),2)
        
        for tag in payload["tags"]:
            exists = recipe.tags.filter(
                name=tag["name"],
                user=self.user
            ).exists()
            self.assertTrue(exists)
    
    def test_create_recipe_with_tag(self):
        """Test create a recipe with existing tag"""
        tag = Tag.objects.create(user=self.user,name="tai")
        payload = {
            "title":"taih recipe",
            "time_minutes":30,
            "price":Decimal("2.50"),
            "tags":[{"name":"tai"},{"name":"breakfeast"}]
        }
        
        res = self.client.post(RECIPES_URL, payload,format="json")
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(),2)
        self.assertIn(tag,recipe.tags.all())
        
        for tag in payload["tags"]:
            exits = recipe.tags.filter(
                name=tag["name"],
                user = self.user
            ).exists()
            self.assertTrue(exits)
               
    def test_create_tag_on_update(self):
        """test creating tag when updating rcipe"""
        recipe = create_recipe(user=self.user)
        
        payload = {"tags":[{"name":"Lunch"}]}
        
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name="Lunch")
        self.assertIn(new_tag,recipe.tags.all())
        
    def test_update_recipe_assign_tag(self):
        """test assigning existing tag when updating recipe"""
        tag = Tag.objects.create(user=self.user,name="Tai")
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        
        tag_lunch = Tag.objects.create(user=self.user,name="Lunch")             
        payload = {
            "tags":[{"name":"Lunch"}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        
        self.assertEqual(res.status_code , status.HTTP_200_OK)
        self.assertIn(tag_lunch,recipe.tags.all()) # tag will be  Lunch 
        self.assertNotIn(tag,recipe.tags.all()) # Tai tag is no longer assigned because wer changed when updating
        
    def test_clear_recipe_tag(self):
        """Test clearing a recipe tags."""
        recipe = create_recipe(user=self.user)
        tag = Tag.objects.create(user=self.user, name="Thai")
        recipe.tags.add(tag)
        
        payload = {"tags":[]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload,format="json")
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(),0)    
        
    
    def test_create_recipe_with_new_ingredients(self):
        """Tets creating a recipe with new ingredients"""
        
        payload = {
            "title" : "choufan",
            "time_minutes" : 12,
            "price" : "23.23",
            "description" : "create a new recipe",
            "ingredients": [
                {
                    "name" : "Tomates"
                },
                {
                    "name" : "Potatoes"
                }
            ]
        }  
        
        res = self.client.post(RECIPES_URL, payload, format="json")
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]   # retreiving a single recipe
        self.assertEqual(recipe.ingredients.count(), 2)
        
        for ingredient in payload["ingredients"]:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=ingredient["name"]
            ).exists()
            self.assertTrue(exists)
            
    def test_create_recipe_with_existing_ingredients(self):
        """Test creating recipe with existing ingredietn""" 
        
        ingredient = Ingredient.objects.create(user=self.user, name="Lemon")
        
        payload = {
            "title": "def",
            "time_minutes" : 12,
            "price" : "23.23",
            "description" : "create a new recipe",
            "ingredients": [
                  {
                      "name":"Lemon"
                  },
                  {
                      "name" : "Kito"
                  }
            ]
        } 
        
        res = self.client.post(RECIPES_URL,payload,format="json")
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  
        recipes = Recipe.objects.filter(user=self.user)     
        self.assertEqual(recipes.count(), 1)  
        recipe = recipes [0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        
    
    def test_create_ingredient_on_update(self):
        """Test creating ingredient when updatin recipe"""
        recipe = create_recipe(user=self.user) 
        
        payload = {
            "ingredients" : [
                {
                    "name" : "dala3"
                }
            ]
        }   
        
        url = detail_url(recipe.id)
        res = self.client.patch(url , payload, format="json") 
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user)
        self.assertIn(new_ingredient,recipe.ingredients.all())
        
    def test_update_recipe_assign_ingredient(self):
        """Test assign exisitng ingredient when updating a recipe"""
        ingredient = Ingredient.objects.create(user=self.user,name="potato")
        
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)
        
        ing2 = Ingredient.objects.create(user=self.user, name="Tomato")
        payload = {
            "ingredients": [
                {
                    "name" : "Tomato"
                }
            ]
        }    
        
        url = detail_url(recipe.id)
        res = self.client.patch(url ,payload, format="json")
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ing2,recipe.ingredients.all())
        self.assertNotIn(ingredient,recipe.ingredients.all())
        
        
    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients"""  
        ingredient = Ingredient.objects.create(user=self.user,name="Tomato")
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)
        
        payload = {
            "ingredients":[]
        }
        
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format="json")
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(),0)
        
    def test_filter_by_tags (self):
        """Filter recipes by tags"""
        r1 = create_recipe(user=self.user,title="dolar") 
        r2 = create_recipe(user=self.user,title="euro") 
        tag1 = Tag.objects.create(user=self.user,name="vegetable")
        tag2 = Tag.objects.create(user=self.user,name="fruit")
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title="Fish and chips")
        
        params = {"tags":f"{tag1.id},{tag2.id}"}
        res = self.client.get(RECIPES_URL,params)
        
        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data) 
    
    def test_filer_by_ingredients(self):
        """Test filtering recipes by ingredients"""
        r1 = create_recipe(user=self.user,title="dala3") 
        r2 = create_recipe(user=self.user,title="mahjouba") 
        r3 = create_recipe(user=self.user,title="zfitti")
        
        ing1 = Ingredient.objects.create(user=self.user,name="ing1") 
        ing2 = Ingredient.objects.create(user=self.user,name="ing2") 
        
        r1.ingredients.add(ing1)
        r2.ingredients.add(ing2)
        
        params = {"ingredients":f"{ing1.id},{ing2.id}"}
        res = self.client.get(RECIPES_URL, params)
        
        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data) 
     
         
class ImageUploadTest (TestCase):
    """Tests for the image upload API"""
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "user@gmail.com",
            "pass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)
        
    def tearDown(self):
        self.recipe.image.delete()
        
    
    def test_upload_image(self):
        """Test uploading image to a recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB",(10,10))
            img.save(image_file,format="JPEG")
            image_file.seek(0)
            payload = {"image":image_file}
            res = self.client.post(url,payload, format="multipart")
            
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn("image",res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))             
        
    
    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""
        
        url = image_upload_url(self.recipe.id)
        payload = {"image":"notimage"}
        res = self.client.post(url,payload,format="multipart")
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            