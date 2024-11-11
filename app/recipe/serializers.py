"""
Serializer for recipe Api
"""

from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""
    class Meta:
        model = Ingredient
        fields = ["id", 'name']
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""
    class Meta:
        model = Tag
        fields = ["id", "name"]  
        read_only_fields = ["id"] 

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)
    
    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags", "ingredients"]
        read_only_fields = ["id"]
    
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)
    
    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients"""
        auth_user = self.context['request'].user
        for ingr in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingr
            )
            recipe.ingredients.add(ingredient_obj)  # Use lowercase 'ingredients'
    
    def create(self, validated_data):
        """Create a recipe"""
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        
        return recipe
    
    def update(self, instance, validated_data):
        """Update a recipe"""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)  # Use lowercase 'ingredients'
        
        # Clear and update tags if provided
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        
        # Clear and update ingredients if provided
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)
        
        # Update other attributes
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
                
        
        
class RecipeDetailSerializer(RecipeSerializer):
    """becuase recipedetailserializer is extention of recipeserializer"""
    
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        
            