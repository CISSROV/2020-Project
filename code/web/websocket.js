

/*
 * websocket.js handles the websocket connections through which
 * data is send through. Html documents that need sensor data
 * should use this js file.
 * 
 * To use:

window.addEventListener("load", function() {
    connect(function(data) {})
}, false);

 * where function takes data and processes it 
 * whatever way the html page needs it
*/

function getHost() {
    // code for getting the hostname / domain name

    // get url
    var tmp = document.location.href

    // remove the http:// or https:// from the url
    if (tmp.startsWith('http://')) {
        tmp = tmp.slice('http://'.length)
    }
    else if (tmp.startsWith('https://')) {
        tmp = tmp.slice('https://'.length)
    }
    else {
        // got a url that starts with something else
        console.error('Weird URL start: ' + tmp)
        return
    }
    // get rid of the path to leave only the domain behind
    // also gets rid of any port number
    return tmp.split('/',1)[0].split(':',1)[0]
}

function connect(dataHandler) {
    //
    // function for handling websockets
    // dataHandler should be a function which takes the received
    // sensor data as an argument. It is called each time data arrives
    //
    // The websocket function assumes that the websocket server 
    // and http server are on the same device
    //
    // make sure all the ports are set to the same number, here 5005 is used
    //
    ws = new WebSocket('ws://' + getHost() + ':5005')

    // tell the ws object what to do when a message arrives
    ws.onmessage = function (event) {
        // hide an error indicator because nothing has gone wrong yet
        document.getElementById('error').hidden = true

        //
        // if the websocket is send hi, it will respond with Hello World!
        // This is for debugging to check if the connection is alive
        //
        // I think this is the function for it but I'm not sure anymore
        // ws.send('hi')
        //
        if (event.data.trim() == 'Hello World!') {
            console.log('Hello World!')
            return
        }

        try {
            // try parsing the json data string
            var data = JSON.parse(event.data)
        }
        catch(err) {
            // log the error
            console.error('JSON parse error')
            // unhide the error indicator to show something went wrong
            document.getElementById('error').hidden = false
            // exit the function
            return
        }

        // call the function given as an argument to do its stuff
        dataHandler(data)
    }

    // tell the ws object what to do upon an (network) error
    ws.onerror = function (event) {
        //console.log('Error')
        // show that there is a problem
        document.getElementById('error').hidden = false
        // try to reconnect in five seconds
        setTimeout(connect, 5000, dataHandler)
    }
    // doesn't display msg if connection is closed by server
}
