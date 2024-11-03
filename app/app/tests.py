from django.test import SimpleTestCase
from .calc import add , subtract

class CalcTests(SimpleTestCase):
    
    def test_calc(self) :
        """Adding number toghether"""
        res = add(5,6)
        
        self.assertEqual(res,11)
        
        
    def  test_subtract(self) : 
        res = subtract(20,10)
        self.assertEqual(res,10)