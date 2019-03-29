// This code is for fetching data to be displayed in a table in json
// The json should be a list of lists with two entries, i.e. like a x by 2 array 

xmlhttp = new XMLHttpRequest()
xmlhttp.onreadystatechange = function() {
  if (this.readyState == 4 && this.status == 200) {
    myObj = JSON.parse(this.responseText)
    txt = document.getElementById("dataTable").innerHTML
    for (x in myObj) {
        txt += "<tr><td>" + myObj[x][0] + "</td><td>" + myObj[x][1] + "</td></tr>"
    }
    document.getElementById("dataTable").innerHTML = txt
  }
}
xmlhttp.open("GET", "data.json", true)
xmlhttp.send()

