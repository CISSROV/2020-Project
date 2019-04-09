

/*
 To use:
 window.addEventListener("load", function() {
    connect(function(data) {})
}, false);
*/

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

function connect(dataHandler) {
    ws = new WebSocket('ws://' + getHost() + ':5005')
    ws.onmessage = function (event) {
        document.getElementById('error').hidden = true
        try {
            var data = JSON.parse(event.data)
        }
        catch {
            console.error('JSON parse error')
            document.getElementById('error').hidden = false
            return
        }
        
        dataHandler(data)
    }
    ws.onerror = function (event) {
        //console.log('Error')
        document.getElementById('error').hidden = false
        setTimeout(connect, 5000, dataHandler)
    }
    // doesn't display msg if connection is closed by server
}
