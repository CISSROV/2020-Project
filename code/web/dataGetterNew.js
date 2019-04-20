// This code is for fetching data to be displayed in a table in json
// The json should be a list of lists with two entries, i.e. like a x by 2 array

var compressed = false;
var localCopy = []

function setData(ls) {
    localCopy.push(ls)

    if (localCopy.length > 200)
    {
        localCopy.shift(1)
    }

    txt = ''
    txt += '<tr><th>Time</th><th>External Temp (&deg;C)</th>'
    txt += '<th>Core Temp (&deg;C)</th><th>Internal Temp (&deg;C)</th>'
    txt += '<th>Heading</th><th>Roll</th><th>Pitch</th><th>Magnetic Field</th>'
    txt += '<th>Acc<sub>x</sub></th><th>Acc<sub>y</sub></th><th>Acc<sub>z</sub></th></tr>'
    cp = [...localCopy]
    for (x in cp.reverse())
    {
        txt += '<tr><td>' + cp[x][0] + '</td><td>' + cp[x][1] + '</td>'
        txt += '<td>' + cp[x][2] + '</td><td>' + cp[x][3] + '</td>'
        txt += '<td>' + cp[x][4] + '</td><td>' + cp[x][5] + '</td>'
        txt += '<td>' + cp[x][6] + '</td><td>' + cp[x][7] + '</td>'
        txt += '<td>' + cp[x][8] + '</td><td>' + cp[x][9] + '</td>'
        txt += '<td>' + cp[x][10] + '</td></tr>'
    }
    document.getElementById('dataTable').innerHTML = txt

    if (compressed) {
        compress()
    }
    document.getElementById('error').hidden = true;
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

window.addEventListener("load", function() {
    connect(setData)
}, false);
