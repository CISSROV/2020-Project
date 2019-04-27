// I really dislike this piece of code and how it does things. But, it works.

// Also, when this is embeded, the js and html can't be accessed so all javascript must happen here!
var indicator = document.getElementById('heading_indicator')
var degs = 0

function rotate(degree) {
    degree = Math.abs(degree)
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

rotate(0)

 window.addEventListener("load", function() {
    connect(function(data) {
        var degree = data[4]
        if (typeof(degree) != 'number') {
            console.error('Got ' + degree + ', expected number')
            document.getElementById('error').hidden = false
        }
        else {
            rotate(degree)
        }
    })
}, false);




