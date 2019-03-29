// This code is for fetching data to be displayed in a table in json
// The json should be a list of lists with two entries, i.e. like a x by 2 array 

var intervalID = 0

function getData() {
    xmlhttp = new XMLHttpRequest()
    xmlhttp.onreadystatechange = function() {
      if ( this.readyState == 4 && this.status == 200 ) {
        myObj = JSON.parse(this.responseText)
        txt = "<table id='dataTable'>"
        txt += "<tr><th>Time</th><th>Temperature (&deg;C)</th></tr>"
        for (x in myObj.reverse()) {
            txt += "<tr><td>" + myObj[x][0] + "</td><td>" + myObj[x][1] + "</td></tr>"
        }
        document.getElementById( "dataTable" ).innerHTML = txt
      }
    }
    xmlhttp.open( "GET", "data.json", true )
    xmlhttp.send()
    //console.log('Update!')
}

function stopUpdating() {
    clearInterval( intervalID )
    document.getElementById( "live" ).style['display'] = 'none'
    document.getElementById( "stop" ).hidden = true
    document.getElementById( "start" ).hidden = false
}

function startUpdating() {
    intervalID = setInterval ( getData, 10000 )
    document.getElementById( "live" ).style['display'] = 'inline'
    document.getElementById( "stop" ).hidden = false
    document.getElementById( "start" ).hidden = true
}

getData()
intervalID = setInterval ( getData, 10000 )




