"""
Views for the recipe API
"""

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from core.models import Recipe, Tag, Ingredient
from .serializers import RecipeSerializer, IngredientSerializer, RecipeDetailSerializer, TagSerializer,RecipeImageSerializer
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response 
from rest_framework.decorators import action


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for the recipe APIs"""
    
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retreieve recipes for authenticated user. """
        queryset = self.queryset
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        
        if tags:
            tags_id = [int(tag) for tag in tags.split(',')]
            queryset = queryset.filter(tags__id__in=tags_id)
        if ingredients:
            ingredients_id = [int(ing) for ing in ingredients.split(',')]
            queryset = queryset.filter(ingredients__id__in=ingredients_id)
        return queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self, *args, **kwargs):
        """return the serialzer class for the reques"""
        if self.action == "list":
            return RecipeSerializer
        elif self.action == "upload_image":
            return RecipeImageSerializer
        else: 
            return RecipeDetailSerializer
    
    def perform_create(self, serializer):
        """create a new recipe"""
        serializer.save(user=self.request.user)
    
    @action(methods=["POST"],detail=True,url_path="upload-image")
    def upload_image(self,request,pk=None):
        """Upload an image to recipe"""
        recie = self.get_object()
        serializer = self.get_serializer(recie,data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)            

class BaseRecipeViewSet(mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """Base ViewSet for recipe attribute"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """filter query set to authenicated user"""
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only",0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by("-name")    
    
class TagViewSet(BaseRecipeViewSet):
    """Viewset for tags"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

        
class IngredientViewSet(BaseRecipeViewSet):
    """Mange ingredients"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
