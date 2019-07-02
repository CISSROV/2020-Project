// This code is for fetching data to be displayed in a table in json
// The json should be a list of lists with two entries, i.e. like a x by 2 array


// requires websocket.js

// determines if the table rows are small or large
var compressed = false
// history of received data points
var localCopy = []

function setData(ls) {
    // 
    // Call this function whenever new data arrives
    // It adds the data to its history of received data (localCopy)
    // and makes an html table with all the data in it, and puts
    // that table into the html document
    //

    // add this data to the list of data received
    localCopy.push(ls)

    // keep only the past 200 data points
    // so if the list is longer than 200,
    // delete the oldest data point
    if (localCopy.length > 200)
    {
        localCopy.shift(1)
    }

    // make the html table
    txt = ''
    txt += '<tr><th>Time</th><th>External Temp (&deg;C)</th>'
    txt += '<th>Core Temp (&deg;C)</th><th>Internal Temp (&deg;C)</th>'
    txt += '<th>Heading</th><th>Roll</th><th>Pitch</th><th>Magnetic Field</th>'
    txt += '<th>Acc<sub>x</sub></th><th>Acc<sub>y</sub></th><th>Acc<sub>z</sub></th></tr>'

    // make a copy of the data list
    cp = [...localCopy]
    // for each data in the list of data
    // in reverse order so the newest appears on top
    for (x in cp.reverse())
    {
        // put all the data points into the table row
        txt += '<tr><td>' + cp[x][0] + '</td><td>' + cp[x][1] + '</td>'
        txt += '<td>' + cp[x][2] + '</td><td>' + cp[x][3] + '</td>'
        txt += '<td>' + cp[x][4] + '</td><td>' + cp[x][5] + '</td>'
        txt += '<td>' + cp[x][6] + '</td><td>' + cp[x][7] + '</td>'
        txt += '<td>' + cp[x][8] + '</td><td>' + cp[x][9] + '</td>'
        txt += '<td>' + cp[x][10] + '</td></tr>'
    }
    // put the table into the html document 
    document.getElementById('dataTable').innerHTML = txt

    // if compressed is set to true
    if (compressed) {
        // make each row smaller so more data fits on a page
        compress()
    }

    // hide the error indicator after successful data processing
    document.getElementById('error').hidden = true;
}

function compress() {
    // makes each table row a bit smaller so more data fits on the screen

    // get all the data points in the table
    var elements = document.getElementsByTagName('td')

    // for each data point
    for (i = 0; i < elements.length; i++)
    {
        // this class reduces the padding of each data point
        elements[i].setAttribute('class','compressed')
    }
    // set the variable for some reason?
    compressed = true

    // hide the compress button
    document.getElementById('compress').hidden = true
    // and show the decompress button which disables this function
    document.getElementById('decompress').hidden = false
}

function decompress() {
    // undo the table row size reduction

    // get all the data points in the table
    var elements = document.getElementsByTagName('td')

    // for each data point
    for (i = 0; i < elements.length; i++)
    {
        // remove the compressed class which makes the rows/ data points smaller
        elements[i].setAttribute('class','')
    }
    // set the variable to false again to disable the compress() function
    compressed = false

    // make the compress button visible again
    document.getElementById('compress').hidden = false
    // hide the uncompress button
    document.getElementById('decompress').hidden = true
}

// start the code once the window / document is fully loaded
window.addEventListener("load", function() {
    // connect is a function of the websocket.js file
    // and handles the websocket connection through which the data is sent
    connect(setData)
}, false);
