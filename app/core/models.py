from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.conf import settings
import uuid
import os


def recipe_image_path(instance, filename):
    """Generate file path for new image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager) : 
    """"Manager for users .."""
    def create_user(self,email,password,**extra_field):
        user = self.model(email=self.normalize_email(email),**extra_field)
        if not email:
            raise ValueError("user must have an email")
        user.set_password(password) # set the encrypt password
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password):
        """create superuser"""
        user = self.create_user(email,password)
        user.is_staff= True
        user.is_superuser= True
        user.save(using=self._db)
        return user
    
    
class User(AbstractBaseUser,PermissionsMixin) :
    """user in the system ...."""
    email = models.EmailField(max_length=255,unique=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
   
    USERNAME_FIELD = "email"
    objects = UserManager()
    

class Recipe(models.Model):
    """recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)    
    description = models.CharField(max_length=255,blank=True)    
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255,blank=True) 
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField("Ingredient")
    image = models.ImageField(null=True,upload_to=recipe_image_path)
    
    def __str__(self):
        return self.title 
    
class Tag(models.Model):
    """Tag for filtering recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )  
    
    def __str__(self):
        return self.name
    
class Ingredient(models.Model):
    """Ingreedient for recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )    
    
    def __str__(self):
        return self.name