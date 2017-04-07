# -*- coding: utf-8 -*-

from django.test import TestCase
                                                                                                                                                                                
# from maraich import settings
from UnitTests import testU_DB, testU_Series, testU_MyTools

        
        
class UnitTests(TestCase):

    def setUp(self):
        pass

    def testMyTools(self):
        self.assertEqual(testU_MyTools.testU_getFloatInPost(), True)

    def testU_DB(self):
        self.assertEqual(testU_DB.testU_DB(), True)

#     def testSeries(self):
#         rep = testU_Series.testU_sauveSerie()
#         

#     
#  
# if __name__ == '__main__':
#  
#     UnitTests().main()
#      
     
