//
// this function for getting the process id is really similar to one found in display.html,
// so maybe they could be combined to avoid having to edit both when changes are made.
//

function checkPID() {
    // get the elements that shows the pid and status
    var pid = document.getElementById('dataCollectionPID')
    var status = document.getElementById('dataCollectionStatus')

    // make a new http request
    xmlhttp = new XMLHttpRequest()
    xmlhttp.onreadystatechange = function() {
        // if the request is complete and returned with 200 OK
        if (this.readyState == 4 && this.status == 200) {
            var txt = this.responseText

            // extract the pid from the html file
            var term = 'id="PID"'
            txt = txt.slice(txt.indexOf(term) + term.length + 6)
            txt = txt.slice(0, txt.indexOf('</p>'))
            
            // set the pid to be the text in the pid element
            pid.innerText = txt
            // if no pid was received from the requested html file set status
            if (txt == 'None') {
                status.innerText = "Not Running"
            }
            else {
                status.innerText = "Running"
            }
        }
        else {
            // request completed but with some error
            if (this.readyState == 4) {
                pid.innerText = "?"
                status.innerText = "?"
                // show error by displaying it in the dump element
                document.getElementById('dump').innerHTML = this.responseText
            }
        }
    }
    // http request type GET
    xmlhttp.open('GET', 'cgi-bin/statusDataCollection.py', true)
    xmlhttp.send()
}

checkPID()
// update the pid every 10 seconds
intervalID = setInterval(checkPID, 10000)
