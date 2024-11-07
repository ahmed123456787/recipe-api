"""Test for the user api"""


from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserTest(TestCase):
    """Test the public user API (in case not authenticated) """
    
    def setUp(self):
        self.client = APIClient()
    
    def test_create_user_success(self) :
        """test creating a user"""
        payload = {
            'email': "test@example.com",
            'password': 'testpass123',
            'name' : 'test name'
        }    
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn("password",res.data)
        
    def test_user_with_email_exist_error(self):
        """test error returned if the user email exists"""
        
        payload = {
            'email': "test@example.com",
            'password': 'testpass123',
            'name' : 'test name'
        }    
        create_user(**payload) # or we can do create_user(email='',password='')
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
    
    def test_short_password(self):
        """Test if password less than 5 chars."""
        payload = {
            'email': "test@example.com",
            'password': 'pw',
            'name' : 'test drf'
        }    
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
    
    def test_create_token_user(self):
        """Test generates token for valid credential"""
        user_details = {
            "name":"ahmed",
            "email" :"te@gmail.com",
            "password":"def123"
        }
        create_user(**user_details)    
        payload = {
            'email': user_details['email'],
            'password' : user_details['password']
        } 
        res = self.client.post(TOKEN_URL,payload)
        self.assertIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
    
    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_email_not_found(self):
        """Test error returned if user not found for given email."""
        payload = {'email': 'test@example.com', 'password': 'pass123'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retreive_user_unauthorized(self):
        """ the authentication is required"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        
# authenticated test 
class PrivetUserApiTest (TestCase):
    """test api that require authentication"""
    
    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            password="testpdd",
            name="test moo"
        )              
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_retreive_profile_success(self):
        """test retreiving profile for logged in user"""
        res =self.client.get(ME_URL)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
    
    def test_post_to_me_not_allowed(self):
        res =self.client.post(ME_URL,{})
        self.assertEqual(res.status_code,status.HTTP_405_METHOD_NOT_ALLOWED) # test that is disable
        
    def test_update_user_profile(self):
        """Test updating the user profile"""
        payload = {"name":'Updated me','password':'ahmed123'}
        res = self.client.patch(ME_URL,payload)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name,payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        
        