"""
Views for the recipe API
"""

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from core.models import Recipe
from .serializers import RecipeSerializer, RecipeDetailSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for the recipe APIs"""
    
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retreieve recipes for authenticated user. """
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self, *args, **kwargs):
        """return the serialzer class for the reques"""
        if self.action == "list":
            return RecipeSerializer
        else: 
            return RecipeDetailSerializer
    
    def perform_create(self, serializer):
        """create a new recipe"""
        serializer.save(user=self.request.user)