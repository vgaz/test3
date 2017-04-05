from maraich.models import Serie, Espece, Legume, Variete
import MyTools 

def testU_DB():
    print ('Début du test', __name__)
    leg = Legume.objects.get(espece__nom="radis rose", variete__nom="flamboyant 3")
    if leg.prodParPied_kg != 0.01:
        return False

    return True

