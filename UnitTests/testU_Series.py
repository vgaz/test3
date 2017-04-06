from django.test import RequestFactory
from maraich import serveRequest
def testU_sauveSerie():
    
    factory = RequestFactory()
        
    # Create an instance of a POST request.   
    request = factory.post(     '/request/', 
                                data={  'cde': ['sauve_serie'],
                                        'id_serie': ['9'], 
                                        'id_legume': ['10'], 
                                        'etalement_recolte_j': ['21'], 
                                        'intra_rang_cm': ['50'],  
                                        'nb_rangs': ['1'], 
                                        'duree_avant_recolte_j': ['50'], 
                                        'date_debut': ['20/05/2017'], 
                                        'b_serre': ['on']}
                                )        

    serveRequest.serveRequest(request)
    return True

