function checkPID() {
    var pid = document.getElementById('dataCollectionPID')
    var status = document.getElementById('dataCollectionStatus')
    xmlhttp = new XMLHttpRequest()
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var txt = this.responseText
            var term = 'id="PID"'
            txt = txt.slice(txt.indexOf(term) + term.length + 6)
            txt = txt.slice(0, txt.indexOf('</p>'))
            //console.log(txt)
            pid.innerText = txt
            if (txt == 'None') {
                status.innerText = "Not Running"
            }
            else {
                status.innerText = "Running"
            }
        }
        else {
            if (this.readyState == 4) {
                pid.innerText = "?"
                status.innerText = "?"
                document.getElementById('dump').innerHTML = this.responseText
            }
        }
    }
    xmlhttp.open('GET', 'cgi-bin/statusDataCollection.py', true)
    xmlhttp.send()
}

checkPID()
intervalID = setInterval(checkPID, 10000)