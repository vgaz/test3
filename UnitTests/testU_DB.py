from maraich.models import Espece, Legume, Variete

def testU_DB():
    print ('Début du test', __name__)
    
    esp = Espece()
    esp.nom="radis rose"
    esp.save()
    
    var = Variete()
    var.nom="a bout bleu"
    var.save()
    
    leg = Legume()
    leg.variete = var
    leg.espece = esp
    leg.prodParPied_kg=0.01
    leg.save()

    
    leg1 = Legume.objects.get(espece__nom="radis rose", variete__nom="a bout bleu")
    if leg1.prodParPied_kg != 0.01:
        return False

    return True

