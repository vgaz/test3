//
// All functions used for payy ci web pages
//
	

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
