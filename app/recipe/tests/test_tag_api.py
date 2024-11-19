"""
Test tags API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Create and return a tag detial"""
    return reverse("recipe:tag-detail",args=[tag_id])

def create_user(email="user@gmail.com",password="test123"):
    """Create and return a user"""
    return get_user_model().objects.create_user(email=email,password=password)

class PublicTagsApiTests(TestCase):
    """Test unathenticated api requests"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """Test auth is required to call tag api"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateTagApiTests(TestCase):
    """Test an authenticated Api requests"""            
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        
    def test_retreive_tags(self):
        """Test retreiving a list"""
        
        Tag.objects.create(user=self.user,name="Vegan")    
        Tag.objects.create(user=self.user,name="Dessert") 
        
        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags,many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
        
    def test_tag_limitedd_to_user(self):
        """Test list of tags is limited to authenticatd user"""
        user2 = create_user(email="def@gmail.com",password="def")
        Tag.objects.create(user=user2,name="define")
        tag = Tag.objects.create(user=self.user,name="Comfort food")
        
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['id'],tag.id)
        self.assertEqual(res.data[0]['name'],tag.name)
               
    def test_upadate_tag(self):
        """test updating a tag"""
        tag = Tag.objects.create(user=self.user,name="define")
        
        payload = {
            "name":"Dessert"
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name,payload["name"])
        
    def test_delete__tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user=self.user,name="define")
        
        url = detail_url(tag.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user) 
        self.assertFalse(tags.exists())    
        
    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags to those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name="Tag1")    
        tag2 = Tag.objects.create(user=self.user, name="Tag2")    
        
        recipe = Recipe.objects.create(
            user=self.user,
            title="reciep",
            time_minutes=12,
            price=Decimal("2.3"),
    
        )
        recipe.tags.add(tag1)
        
        res = self.client.get(TAGS_URL, {'assigned_only':1})
        
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        
        self.assertIn(s1.data,res.data)
        self.assertNotIn(s2.data,res.data)