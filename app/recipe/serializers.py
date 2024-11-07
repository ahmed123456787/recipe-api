"""
Serializer for recipe Api
"""

from rest_framework import serializers
from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""
    price = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        model = Recipe
        fields = ["id", 'title', "time_minutes", "price", "link"]
        read_only_fields = ['id']
        

class RecipeDetailSerializer(RecipeSerializer):
    """becuase recipedetailserializer is extention of recipeserializer"""
    
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        
            