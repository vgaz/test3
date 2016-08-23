//
// gestion des planches, séries et evts
//
	
   
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
   
    
function majListEvts(id_serie)
    {
    // recup evts du serie
    s_request = "cde=getEvtsSerie&id=" + id_serie
    rep = requestServer(s_request)  
    jsonRep = JSON.parse(rep)

    if (jsonRep.status == true)
        {
        s_debut = ""
        s_fin = ""
        s_evts = '<table border="1" width="100%">\n'
        // récuperation de tous les evenements
        for(ii=0;ii<jsonRep.l_evts.length;ii++)
            {
            d_evt = jsonRep.l_evts[ii].fields
            s_evts += "<tr><td> " + d_evt.date + " </td><td> " + d_evt.duree_j + "j </td><td> "  + d_evt.nom + " </td>"
            s_evts += "<td><a href='javascript:editeEvenement(" + d_evt.id + ")'><img align='right' src='{{STATIC_URL}}images/editor.png' title='Editer'></a></td>"
            s_evts += "<td><a href='javascript:supprimeEvenement(" + d_evt.id + ")'><img align='right'src='{{STATIC_URL}}images/toDelete.jpeg' title='Supprimer'></a></td></tr>"
            }
          
        s_evts += s_debut + s_fin + "</table>\n"
        }
    else
        alert("err")
        
    document.getElementById("editeSerie_evts").innerHTML = s_evts
    }
    

function  deplacement(hForm)
    {
	//appel serveRequest 
    s_request = "cde=deplacement_serie&id_serie=" + document.getElementById("deplacement_id_serie").value
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
    