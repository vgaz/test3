//
// All functions used for payy ci web pages
//
	

function debutPatienter()
    {
    // on place au niveau du pointeur dans l'ecran
    //e.clientX  e.clientY
    // on allume le gif
    hGif = document.getElementById("waiting")
    hGif.style.display="block"
    }
    
function finPatienter()
    {    
    // on eteint le gif
    hGif = document.getElementById("waiting")
    hGif.style.display="none"
    }
    
function checkConnexion()
	{
	rep = requestServer('expert_mode=get_status')
	if (rep == "True")
		{
			txt = "Your're now connected in expert mode. It gives you more rights to manage CI results."
			document.getElementById('connexion').innerHTML = "<a href='#' onclick='requestServer(" + '"expert_mode=quit"' + ");window.location.reload()'>Quit expert mode</a>"
			document.getElementById('login').innerHTML = "<p>" + txt + "</p><br /><p><a href='../home'>Home</a></p>"
		}
	if (rep == "False")
		document.getElementById('connexion').innerHTML = "<a href='../expert_mode_login/'>Connexion in expert mode</a>"
	}

function getValueOfTagName(root, tagName, attrName)
	{
	// get value of <tagName name="attrName" value="the value that will be returned"
	if (root == null)
		l_elts = document.getElementsByTagName(tagName)
	else
		l_elts = root.getElementsByTagName(tagName)

		
	// return the first value of tag name element
	for(ii=0; ii < l_elts.length; ii++)
		if (l_elts[ii]["name"] == attrName)
			return (l_elts[ii]["value"])

	return ("")
	}
	



function setValueOfTagName(root, tagName, attrName, value)
	{
	// set value of <tagName name="attrName" value"the value that will be set"
	if (root == null)
		l_elts = document.getElementsByTagName(tagName)
	else
		l_elts = root.getElementsByTagName(tagName)

		
	// set the first attribute value of tag name element
	for(ii=0; ii < l_elts.length; ii++)
		if (l_elts[ii]["name"] == attrName)
			l_elts[ii]["value"] = value

	}
	
	
function requestServer(param)
	{

	url = window.location.protocol + '//' + window.location.host + window.location.pathname + '../request/'

	hReq = new XMLHttpRequest();
	hReq.open("POST", url , false)
	//hReq.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
    hReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
	token = getValueOfTagName(null, "input", "csrfmiddlewaretoken")
	if (token != "")
		hReq.setRequestHeader('X-CSRFToken', token)
	hReq.onreadystatechange=function()
  		{
  		// la fonction de prise en charge du retour
		if ((hReq.readyState==4) && (hReq.status==200))		
			{
			return hReq.responseText;
			}
		else
			{
			msg = "bad server return, req status = " + hReq.status;
			alert(msg);
			return msg;
			}
  		}
	hReq.send(param)

	return hReq.responseText
 	}


function validateAndRunJob(s_vmVersion, s_debug)
	{
	oSelectOne = manualRunForm.elements["elt_suiteList"]
	index = oSelectOne.selectedIndex
	suite = oSelectOne.options[index].text                
	oSelectOne = manualRunForm.elements["elt_whenList"]
	index = oSelectOne.selectedIndex
	when = oSelectOne.options[index].text
                    
	if( confirm('Do you confirm the planification of the test suite\n' + suite + '\n' + when + '\non the ' + s_vmVersion))
		{
        url ='./index.py?planified=add&vmVersion=' + s_vmVersion + '&suiteName=' + suite + '&when=' + when + s_debug
        window.open(url, '_self')
        }
    }
    
function supprime_planche(plId)
    {
    s_request = "cde=supprime_planche&id=" + plId
    rep = requestServer(s_request)  
    jsonRep = JSON.parse(rep)
    if (jsonRep.status != 'true')
        alert(jsonRep.err)
    }
    
function prepareDeplacementImplantation(id_serie, id_implantation, nbPieds, id_plancheDest)
    {
    // boite de dialogue de confirmation de déplacement avant requete serveur
    hDiv = document.getElementById("divDeplacementImplantation")
    //hDiv.style.display = "block"
    hDivImpl = document.getElementById(id_implantation)
    document.getElementById("deplacement_id_serie").value = id_serie
    document.getElementById("deplacement_id_implantation").value = id_implantation
    document.getElementById("deplacement_id_planche_dest").value = id_plancheDest
    document.getElementById("deplacement_nb_rangs").value = hDivImpl.getAttribute("nb_rangs")
    document.getElementById("deplacement_intra_rang_cm").value = hDivImpl.getAttribute("intra_rang_cm")
    document.getElementById("deplacement_nb_pieds").value = nbPieds
    deplaceImplantation()
    }

  
  
function  deplaceImplantation()
    {
    // déplacement d'une implantation vers une autre planche 
    s_request = "cde=deplacement_implantation&id_serie=" + document.getElementById("deplacement_id_serie").value
    s_request += "&id_implantation=" + document.getElementById("deplacement_id_implantation").value
    s_request += "&id_planche_dest=" + document.getElementById("deplacement_id_planche_dest").value
    s_request += "&nb_pieds=" + document.getElementById("deplacement_nb_pieds").value
    s_request += "&nb_rangs=" + document.getElementById("deplacement_nb_rangs").value
    s_request += "&intra_rang_cm=" + document.getElementById("deplacement_intra_rang_cm").value

    rep = requestServer(s_request + "&simulation=true")
    jsonRep = JSON.parse(rep)
    document.getElementById("divDeplacementImplantation").style.display = "none"
    
    if (jsonRep.status == true)
        {
        if (confirm(jsonRep.msg +  "\n\nVoulez-vous continuer et effectuer l'opération ?"))
            {
            rep = requestServer(s_request + "&simulation=false")
            jsonRep = JSON.parse(rep)
            if (jsonRep.status == false)
                alert(jsonRep.msg)
            window.location.reload()
            }
        }        
    else
        {
        document.getElementById("divInfoDebug").innerHTML = jsonRep.msg
        alert(jsonRep.msg)
        }
    }     