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


function checkProfForm()
{
	bDisableSubmit = false

	// check if almost one rack is selected
	l_rep = document.getElementsByClassName("InputList")
	
	for (ii=0; ii< l_rep.length; ii++) 
		{
		l_inputs = l_rep[ii].getElementsByTagName("input");
		bOneCheckedAtLeast = false;
		for (i=0; i< l_inputs.length; i++) 
			{
			if (l_inputs[i].checked == 1)
				{
				bOneCheckedAtLeast = true;
				break;
				}
			}
		if (bOneCheckedAtLeast == false)
			{
			l_rep[ii].style.borderColor = "red";
			bDisableSubmit = true
			}
		else
			l_rep[ii].style.borderColor = "white";
		}

	if (bDisableSubmit)
		document.forms.mainForm.submit.disabled = true
	else
		document.forms.mainForm.submit.disabled = false
					
}

function colorScores()
	{
	// change background color for all elements with class score depending on attribute "ratio"
	l_rep = document.getElementsByClassName("score");

	for (i=0; i < l_rep.length; i++) 
		l_rep[i].style.backgroundColor = getScoreColor( parseInt(l_rep[i].getAttribute("ratio")))
	

}


function getValueOfTagName(root, tagName, attrName)
	{
	// get value of <tagName name="attrName" value"the value that will be returned"
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



function showHideEquals(buttonName, rawName)
	{
    button = document.getElementsByName(buttonName)
        
    l_elt = document.getElementsByName(rawName)  // find all elements
    if (button[0].value=='Show all')
    	{
    	newstyle = ""
        button[0].value="Hide equals"
    	for (ii=0; ii<l_elt.length; ii++)
        	l_elt[ii].style.display = newstyle
    	}
    else
        // hide equal scores
    	{
    	button[0].value = "Show all"
    	for (ii=0; ii<l_elt.length; ii++) 
        	{
            l_td = l_elt[ii].getElementsByClassName('score')   
            bEquals = true
            for (iii=0; iii<l_td.length; iii++)
        		{
            	if ( (l_td[0].getAttribute('nb_tests_ok') != l_td[iii].getAttribute('nb_tests_ok')) || (l_td[0].getAttribute('nb_tests_ko') != l_td[iii].getAttribute('nb_tests_ko')))
            		{
            		bEquals = false
            		break
            		}	
        		}
        	if (bEquals == true)
        		l_elt[ii].style.display = "none"
        	}    	
    	}
	}


function uploadComment(bin_version)
    {
    comment = document.getElementById('txtarea_general_comment').value.replace("\n", "\\n")
    request = 'set_bin_version_comment={"bin_version":"' + bin_version + '","comment":"' + comment + '"}'
    document.getElementById('txtarea_general_comment').innerHTML = requestServer(request)
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
