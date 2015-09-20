//
// gestion des planches, plants et evts
//
	

function editePlant(hPlant)
    {
    // recup evenements liés à ce plant
    id_plant = hPlant.getAttribute("id")
    
    document.getElementById('divEditEvenement').style.display = 'inline'
    
    if (id_plant.search("_") != 1)
        majListEvts(id_plant)
        
    // maj variété
    id_variet  = hPlant.getAttribute("variete")
    list = document.getElementById("editPlant_select_var").getElementsByTagName("option")
    for(ii=0;ii<list.length;ii++)
        if (list[ii].value == id_variet)
            {
            document.getElementById("editPlant_select_var").options[ii].selected=true
            break
           }

    // maj attributs plant                   
    document.getElementById("editPlant_id_planche").innerHTML = "A FAIRE"
    document.getElementById("editPlant_plantId").innerHTML = id_plant
    document.getElementById("editPlant_quantite").value = hPlant.getAttribute("quantite")
    document.getElementById("editPlant_date_debut").value =  hPlant.getAttribute("date_debut")
    document.getElementById("editPlant_date_fin").value =  hPlant.getAttribute("date_fin")
    document.getElementById("divEditPlant").style.display = "inline"
    }
        

    
function changelePas(delta)
{
    decalage_j += delta
    if (decalage_j < 1) decalage_j = 1
    document.getElementById("decalage_j").value = decalage_j
}


function getTicket()
{
    g_index_ticket += 1
    return(g_index_ticket) 
}
   
    
function majListEvts(id_plant)
    {
    // recup evts du plant
    s_request = "cde=getEvtsPlant&id="+ id_plant
    rep = requestServer(s_request)  
    jsonRep = JSON.parse(rep)
    s_debut = ""
    s_fin = ""
    s_evts = '<table border="0" width="100%">\n'
    if (jsonRep.status == 'true' )
        {
        //recuperation de tous les evenements, on met en gras le debut et fin
        for(ii=0;ii<jsonRep.l_evts.length;ii++)
            {
            s_evts += "<tr><td><b>" +  o_nomTypeEvt[jsonRep.l_evts[ii].type] +" </b> " + jsonRep.l_evts[ii].date + " (" + jsonRep.l_evts[ii].duree_j + "j) "  + jsonRep.l_evts[ii].nom + "</td>"
            s_evts += "<td><a href='javascript:editeEvenement(" + jsonRep.l_evts[ii].id + ")'><img align='right' src='{{STATIC_URL}}images/editor.png' title='Editer'></a></td>"
            s_evts += "<td><a href='javascript:supprimeEvenement(" + jsonRep.l_evts[ii].id + ")'><img align='right'src='{{STATIC_URL}}images/toDelete.jpeg' title='Supprimer'></a></td></tr>"
            }
        }    
    s_evts += s_debut + s_fin + "</table>\n"

    document.getElementById("editPlant_evts").innerHTML = s_evts
    }
    
function  editeDeplacement(id_plant_orig)
    {
    	hPlant = document.getElementById(id_plant_orig)
    	hDivDepl = document.getElementById("div_deplacement_plants")
    	hDivDepl.style.display = "block"
    	hDivDepl.style.left = "10px"
    	document.getElementById("deplacement_variete").innerHTML = hPlant.getAttribute("nom_variete")
    	document.getElementById("deplacement_id_plant").value = id_plant_orig
    	document.getElementById("deplacement_intra_rang_cm").value = hPlant.getAttribute("intra_rang_cm")
    	document.getElementById("deplacement_nb_rangs").value = hPlant.getAttribute("nb_rangs")
    	hDivDepl.style.top = hPlant.offsetTop + "px"
//    	alert ("id planche = " + hPlant.parentNode.getAttribute("id"))

    }    
function  deplacement(hForm)
    {
	//appel serveRequest 
    s_request = "cde=deplacement_plant&id_plant=" + document.getElementById("deplacement_id_plant").value
    s_request += "&id_planche_src=0"
    s_request += "&num_planche_dest=" + document.getElementById("deplacement_num_planche_dest").value
    s_request += "&nb_rangs=" + document.getElementById("deplacement_nb_rangs").value
    s_request += "&intra_rang_cm=" + document.getElementById("deplacement_intra_rang_cm").value
    s_request += "&deplacement_partiel=" + document.getElementById("deplacement_partiel").checked
    s_request += "&nb_plants=" + document.getElementById("deplacement_nb_plants").value
    b_simu = document.getElementById("deplacement_simulation").checked
    s_request += "&simu=" + b_simu
    rep = requestServer(s_request)  
    jsonRep = JSON.parse(rep)
    if (jsonRep.status == 'true')
        {
        document.getElementById("div_deplacement_plants").style.display = "none"
      	alert(jsonRep.msg)
        if (b_simu == "false")
        	{
        	// on rafraichit la page
        	window.location.replace(window.location.pathname)
        	}
        }
    else
    	document.getElementById("divInfoDebug").innerHTML = jsonRep.err
    }
    