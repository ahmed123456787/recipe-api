"""Test for the Django admin modifications"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


class AdminSiteTests(TestCase):
    """test for django admin"""
    
    def setUp(self):
        """Create suer and client"""
        self.client= Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password="test123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="test123",
            username="test user"
        )
    def test_users(self):
        """Test that user are listed on page"""
        url = reverse("admin:core_user_changelist") 
        res = self.client.get(url)   
        self.assertContains(res,self.user.username)
    
    def test_edit_user_page(self):
        """test the edit user page works"""
        url = reverse('admin:core_user_change',args=[self.user.id])
        res = self.client.get(url)
        
        self.assertEqual(res.status_code,200)
            
    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code,200)
                