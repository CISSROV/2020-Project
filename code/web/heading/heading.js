// I really dislike this piece of code and how it does things. But, it works.

// Also, when this is embeded, the js and html can't be accessed so all javascript must happen here!
var indicator = document.getElementById('heading_indicator')
var degs = 0

function rotate(degree) {
    if (degree < 0 || degree > 360) {
        document.getElementById('error').hidden = false
        throw new Error('Degree Argument out of Range, got ' + degree)
    }
    if (degs - degree < -180) {// example: degs: 0 - degree: 350 = -350 < -180, degree -= 360, degree == -10
        degree -= 360
    }
    if (degs - degree > 180) {// example: degs: 350 - degree: 0 = 350 > 180, degree += 360, degree == 360
        degree += 360
    }
    var rules = document.styleSheets[0].rules

    for (var i = 0; i < rules.length; i++) {
        if (rules[i].selectorText == '#heading_indicator.move') {
            document.styleSheets[0].removeRule(i)
            break
        }
    }
    document.styleSheets[0].insertRule('#heading_indicator.move {transition: 1s;transform: rotateZ(' + (degree) + 'deg) !important;}')
    degs = degree
}

/*
function spin() {
    if (degs + 20 > 360) {
        degs = -20
    }
    rotate(degs + 20)

}
intervalID = setInterval(spin, 1000)
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

var ws = null

function connect() {
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
        
        var degree = data[4]
        if (typeof(degree) != 'number') {
            console.error('Got ' + degree + ', expected number')
            document.getElementById('error').hidden = false
        }
        else {
            rotate(degree)
        }
    }
    ws.onerror = function (event) {
        //console.log('Error')
        document.getElementById('error').hidden = false
        setTimeout(connect, 5000)
    }
    // doesn't display msg if connection is closed by server
}

rotate(0)
connect()




