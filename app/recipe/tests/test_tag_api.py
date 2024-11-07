"""
Test tags API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")

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
        user2 = create_user(email="def@gmail.com",name="def")
        Tag.objects.create(user=user2,name="define")
        tag = Tag.objects.create(user=self.user,name="Comfort food")
        
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data).data,1)
        self.assertEqual(res.data[0]['id'],tag.id)
        self.assertEqual(res.data[0]['name'],tag.name)
               
        