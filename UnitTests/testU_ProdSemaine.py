from maraich.models import Serie
import MyTools 

def testU_ProdSemaine():
    print ('DEBUT du test', __name__)
    date_debut = MyTools.getDateFrom_d_m_y("26/05/2017")
    serie = Serie.objects.get(id=7)
    print (serie.descriptif())
    print (serie.prodHebdo(date_debut))

#     b1 = respecteRotation(date_debut, 1, 1)
             
    return True

