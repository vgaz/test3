from django.test import RequestFactory
import MyHttpTools

def testU_getFloatInPost():

    factory = RequestFactory()

    # Create an instance of a POST request.
    request = factory.post('/recolte/', 
                                
                                data={"periode":"specifique",
                                      "date_debut_vue":"03/04/2017",
                                      "date_fin_vue":"15/4/2017", 
                                      "toto":"otttn",
                                      "faa":3.4

                                    }
                                )
    if MyHttpTools.getFloatInPost(request, "faea", 1.2) != 1.2:
        return False
    
    if MyHttpTools.getFloatInPost(request, "faa") != 3.4:
        return False
    
    try:
        ret = False
        MyHttpTools.getFloatInPost(request, "faeax")
    except:
        ret = True
         

    return ret

