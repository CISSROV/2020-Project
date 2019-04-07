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
intervalID = setInterval (checkPID, 10000)

function startDataCollection() {
    var status = document.getElementById('startDataCollectionStatus')
    var otherStatus = document.getElementById('dataCollectionStatus')
    var button = document.getElementById('startDataCollectionButton')
    button.innerText = "Running"
    status.innerHTML = "Starting..."
    
    xmlhttp = new XMLHttpRequest()
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            //console.log(this.responseText)
            if (this.responseText.toLowerCase().indexOf('error') != -1) {
                // an error has occured
                button.innerText = "Start"
                otherStatus.innerHTML = "?"
                status.innerHTML = "Error in Shell"
                document.getElementById('dump').innerText = this.responseText
            }
            else {
                // no error
                otherStatus.innerHTML = "Starting..."
                status.innerHTML = "Task Complete"
                button.innerText = "Start"
            }
        }
        else {
            if (this.readyState == 4) {
                button.disabled = false
                button.innerText = "Start"
                otherStatus.innerHTML = "?"
                status.innerHTML = "Error " + this.status
                document.getElementById('dump').innerHTML = this.responseText
            }
        }
    }
    xmlhttp.open('GET', 'cgi-bin/startup.py', true)
    xmlhttp.send()
}

function stopDataCollection() {
    var status = document.getElementById('stopDataCollectionStatus')
    var otherStatus = document.getElementById('dataCollectionStatus')
    var button = document.getElementById('stopDataCollectionButton')
    button.innerText = "Running"
    status.innerHTML = "Stopping..."
    
    xmlhttp = new XMLHttpRequest()
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            //console.log(this.responseText)
            if (this.responseText.toLowerCase().indexOf('error') != -1) {
                // an error has occured
                button.innerText = "Stop"
                otherStatus.innerHTML = "?"
                status.innerHTML = "Error in Shell"
                document.getElementById('dump').innerText = this.responseText
            }
            else {
                // no error
                otherStatus.innerHTML = "Stopping..."
                status.innerHTML = "Task Complete"
                button.innerText = "Stop"
            }
        }
        else {
            if (this.readyState == 4) {
                button.disabled = false
                button.innerText = "Stop"
                otherStatus.innerHTML = "?"
                status.innerHTML = "Error " + this.status
                document.getElementById('dump').innerHTML = this.responseText
            }
        }
    }
    xmlhttp.open('GET', 'cgi-bin/shutdown.py', true)
    xmlhttp.send()
}
