// This code is for fetching data to be displayed in a table in json
// The json should be a list of lists with two entries, i.e. like a x by 2 array 

var compressed = false;
var localCopy = []


function setData(ls) {
    localCopy.push(ls)

    txt = ''
    txt += '<tr><th>Time</th><th>External Temp (&deg;C)</th>'
    txt += '<th>Core Temp (&deg;C)</th><th>Internal Temp (&deg;C)</th>'
    txt += '<th>Heading</th><th>Roll</th><th>Pitch</th><th>Magnetic Field</th>'
    txt += '<th>Acc<sub>x</sub></th><th>Acc<sub>y</sub></th><th>Acc<sub>z</sub></th></tr>'
    for (x in localCopy.reverse()) 
    {
        txt += '<tr><td>' + localCopy[x][0] + '</td><td>' + localCopy[x][1] + '</td>'
        txt += '<td>' + localCopy[x][2] + '</td><td>' + localCopy[x][3] + '</td>'
        txt += '<td>' + localCopy[x][4] + '</td><td>' + localCopy[x][5] + '</td>'
        txt += '<td>' + localCopy[x][6] + '</td><td>' + localCopy[x][7] + '</td>'
        txt += '<td>' + localCopy[x][8] + '</td><td>' + localCopy[x][9] + '</td>'
        txt += '<td>' + localCopy[x][10] + '</td></tr>'
    }
    document.getElementById('dataTable').innerHTML = txt

    if (compressed) {
        compress()
    }
    document.getElementById('dataError').hidden = true;
}

function compress() {
    var elements = document.getElementsByTagName('td')
    for (i = 0; i < elements.length; i++)
    {
        elements[i].setAttribute('class','compressed')
    }
    compressed = true

    document.getElementById('compress').hidden = true
    document.getElementById('decompress').hidden = false
}

function decompress() {
    var elements = document.getElementsByTagName('td')
    for (i = 0; i < elements.length; i++)
    {
        elements[i].setAttribute('class','')
    }
    compressed = false

    document.getElementById('compress').hidden = false
    document.getElementById('decompress').hidden = true
}

function getHost() {
    // code for getting the hostname / domain name
    var tmp = document.location.href
    if (tmp.startsWith('http://')) {
        tmp = tmp.slice('http://'.length)
    }
    else if (tmp.startsWith('https://')) {
        tmp = tmp.slice('https://'.length)
    }
    else {
        console.error('Weird URL start: ' + tmp)
        return
    }
    return tmp.split('/',1)[0].split(':',1)[0]
}

function connect() {
    ws = new WebSocket('ws://' + getHost() + ':5005')
    ws.onmessage = function (event) {
        document.getElementById('dataError').hidden = true
        try {
            var data = JSON.parse(event.data)
        }
        catch {
            console.error('JSON parse error')
            document.getElementById('dataError').hidden = false
            return
        }
        
        setData(data)
    }
    ws.onerror = function (event) {
        //console.log('Error')
        document.getElementById('dataError').hidden = false
        setTimeout(connect, 5000)
    }
    // doesn't display msg if connection is closed by server
}

connect()
