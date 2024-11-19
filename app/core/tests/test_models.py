""""Test for models"""


from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models


def create_user(email="user@example.com",password="password123"):
    user = get_user_model().objects.create_user(email,password)  
    return user  

class ModelTest (TestCase):
    """test the user """
    def test_create_user_with_email(self) :
        """testig creatinf a user with an email successful"""
        email = "test@example.com"
        password= "test123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))
    
    def test_new_user_email_norm(self):
        """Test email is normlized"""
        sample_email = [
            ['test1@EXAMPLE.com','test1@example.com'],
            ['test2@EXample.com','test2@example.com'],
        ]
        for email,expected in sample_email:
            user = get_user_model().objects.create_user(email,'sample123')
            self.assertEqual(user.email,expected)
    
    def test_new_user_without_email(self):
        """Test that creating user without email will raise an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','test123')  
            
    def test_create_super_user(self) :
        """test creating a super user"""
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123"
        ) 
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
    def test_create_recipe(self):
        """Test creating a recipe is successful"""
        user = get_user_model().objects.create_user(
            "test@example.com",
            "test123"
        )   
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe',
            time_minutes=5,
            price=Decimal("5.5"),
            description="description recipe",
        )  
        self.assertEqual(str(recipe),recipe.title)
    
    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()
        tag = models.Tag.objects.create(user=user,name="Tag1")
        
        self.assertEqual(str(tag),tag.name)    
        
    def test_create_ingredient(self):
        """Test creating an ingredient"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user = user,
            name= "Ingredient1"
        ) 
        
        self.assertEqual(str(ingredient),ingredient.name)   
    
    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self,mock_uuid):
        """Test generating image paths"""
        
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
        