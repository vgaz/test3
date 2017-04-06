

function getScoreColor(percentScore)
{
    // return a tupple of rgb color from a given perecnt score
	// percentScoreis INT
	
    if (percentScore < 0 || percentScore > 100)
        return [255, 255, 255]
    
    if (percentScore < 75)
    {
    	//# dégradé de rouge pur à orange clair (= 255,231,0)
        i_r = 255 
        i_g = (percentScore * 231) / 75
        i_b = 0
	}
    else
    {
    	//# dégradé de orange clair (= 255,231,0) à vert pur
        i_r = 255 - 255 * (percentScore - 75) / 25 
        i_g = 231 + (255 - 231) * (percentScore - 75) / 25
        i_b = 0
    }
    
    i_r = Math.floor( i_r)
    i_g = Math.floor( i_g)
    i_b = Math.floor( i_b)
    return ("rgb(" + i_r + "," + i_g + "," + i_b + ")")
		
}
	
function colorScores()
	{
	// change background color for all elements with class score depending on attribute "ratio"
	l_rep = document.getElementsByClassName("score");

	for (i=0; i < l_rep.length; i++) 
		l_rep[i].style.backgroundColor = getScoreColor( parseInt(l_rep[i].getAttribute("ratio")))
	

}
