from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_ingredient( user, name ):
    return Ingredient.objects.create( user=user, name=name )

def create_recipe( user, title, time_minutes, price ):
    return Recipe.objects.create( title=title, time_minutes=time_minutes, price=price, user=user )

class PublicIngredientsApiTests( TestCase ):
    """Test the publicly available ingredients API"""

    def setUp( self ):
        self.client = APIClient()
    
    def test_login_required( self ):
        """Test that login is required to access the end-point"""
        res = self.client.get( INGREDIENTS_URL )

        self.assertEqual( res.status_code, status.HTTP_401_UNAUTHORIZED )

class PrivateIngredientsApiTests( TestCase ):
    """Test the private ingredients API"""

    def setUp( self ):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate( self.user )
    
    def test_retrieve_ingredient_list( self ):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create( user = self.user, name = 'Kale' )
        Ingredient.objects.create( user = self.user, name = 'Salt' )

        res = self.client.get( INGREDIENTS_URL )

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer( ingredients, many = True )
        self.assertEqual( res.status_code, status.HTTP_200_OK )
        self.assertEqual( res.data, serializer.data )

    def test_ingredients_limited_to_user( self ):
        """Test that only ingredients for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Ingredient.objects.create( user = user2, name = 'Vinegar' )
        ingredient = Ingredient.objects.create( user = self.user, name = 'Tumeric' )

        res = self.client.get( INGREDIENTS_URL )

        self.assertEqual( res.status_code, status.HTTP_200_OK )
        self.assertEqual( len( res.data ), 1 )
        self.assertEqual( res.data[0]['name'], ingredient.name )

    def test_create_ingredient_successful( self ):
        """Test create a new ingredient"""
        payload = {
            'name': 'Cabbage'
        }
        self.client.post( INGREDIENTS_URL, payload )

        exists = Ingredient.objects.filter(
            user = self.user,
            name = payload['name'],
        ).exists

        self.assertTrue( exists )
    
    def test_create_ingredient_invalid( self ):
        """Test creating invalid ingredient fails"""
        payload = {
            'name': ''
        }
        res = self.client.post( INGREDIENTS_URL, payload )

        self.assertEqual( res.status_code, status.HTTP_400_BAD_REQUEST )
    
    def test_retrieve_ingredients_assigned_to_recipes( self ):
        """Test filtering ingredients by those assigned to recipes"""

        ingredient1 = create_ingredient( self.user, 'Apples' )
        ingredient2 = create_ingredient( self.user, 'Turkey' )

        recipe = create_recipe( self.user, 'Apple crumble', 5, 10 )

        recipe.ingredients.add( ingredient1 )

        res = self.client.get( INGREDIENTS_URL, { 'assigned_only': 1 } )

        serializer1 = IngredientSerializer( ingredient1 )
        serializer2 = IngredientSerializer( ingredient2 )
        self.assertIn( serializer1.data, res.data )
        self.assertNotIn( serializer2.data, res.data )
    
    def test_retrieve_ingredients_assigned_unique( self ):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = create_ingredient( self.user, 'Eggs' )
        Ingredient.objects.create( user=self.user, name='Cheese' )
        
        recipe1 = create_recipe( self.user, 'Eggs benedict', 30, 12.00 )
        recipe1.ingredients.add( ingredient )
        
        recipe2 = create_recipe( self.user, 'Coriander eggs on toast', 20, 5.00 )
        recipe2.ingredients.add( ingredient )

        res = self.client.get( INGREDIENTS_URL, { 'assigned_only': 1 } )

        self.assertEqual( len( res.data ), 1 )