template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Neuvotteluhuoneet</title>
    <meta http-equiv="refresh" content="120" >
    <link rel="stylesheet" href="./stylesheet.css"/>
</head>
<body>
    <div id="textbox">
    <p class="headline">NEUVOTTELUHUONEET</p>
    <p id="datetime" class="text"></p>
    </div>
    <div style="clear: both;"></div>
    <p id="meeting_content">
    %REPLACE_THIS_WITH_CONTENT%
    </p>

    <script language="javascript">
        function init() {
            updateClock();
        }

        function updateClock() {
            var currentTime = new Date()
            var year = currentTime.getFullYear()
            var month = currentTime.getMonth() + 1;
            var day = currentTime.getDate();
            var hours = currentTime.getHours();
            var minutes = currentTime.getMinutes();
            var seconds = currentTime.getSeconds();

            if (minutes < 10){
            minutes = "0" + minutes
            }
            if (seconds < 10){
            seconds = "0" + seconds
            }

            document.getElementById('datetime').innerHTML = [day + "." + month + "." + year + " " + hours + ":" + minutes];
            setTimeout(updateClock, 1000);
        }

        window.onload = init();
    </script>
</body>
</html>"""

css_template = """html, body {
    position: relative;
    height: 100%;
    background: #00b0db;
    font-family: calibri, Helvetica Neue, Helvetica, Arial;
    font-size: 14px;
    color:#000;
    margin: 0px;
    padding: 0px;
    overflow: hidden;
}
table {
    border-spacing: 0px 0px;
    border-color: white;
    table-layout: fixed;
    position: absolute;
    top: 10vh;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 90vh;
}
th, td {
    padding-left: 1em;
    text-align: left;
    border-bottom: solid 4px white;
    color: white;
    height: 2vh;
}
.headline {
    font-family: calibri;
    font-size: 41px;
    color: white;
    float:left;
    padding-left: 1em;
}
.headline_archive {
    font-size: 41px;
    color: white;
    margin-top: 50px;
    margin-bottom: 10px;
}
.text {
    font-size: 41px;
    color: white;
    float: right;
    padding-right: 1em;
}

.meetingroom {
    font-family: calibri;
    font-size: 32px;
    color: white;
    border-right: solid 4px white;
    border-bottom: solid 4px white;
    padding-top: 30px;
    padding-left: 1em;
    padding-bottom: 30px;
}
.event_name {
    font-family: calibri;
    font-size: 32px;
    color: white;
    border-right: solid 4px white;
    border-bottom: solid 4px white;
    padding-top: 20px;
    padding-bottom: 20px;
}
.event_info {
    font-family: calibri;
    font-size: 24px;
    color: white;
    border-bottom: solid 4px white;
    padding-left: 1em;
    padding-top: 10px;
    padding-bottom: 10px;
    line-height: 125%;
}
.event_primary {
    font-family: calibri;
    font-size: 24px;
    color: white;
    border-bottom: solid 4px white;
    padding-left: 1em;
    padding-top: 10px;
    padding-bottom: 10px;
    line-height: 125%;
}
.event_secondary {
    font-family: calibri;
    font-size: 24px;
    color: white;
    border-bottom: solid 4px white;
    padding-left: 1em;
    padding-top: 10px;
    padding-bottom: 10px;
    line-height: 125%;
}
.eventdate {
    font-family: calibri;
    font-size: 26px;
    color: white;
    border-bottom: solid 4px white;
    border-right: solid 4px white;
}
.eventdate_primary {
    font-family: calibri;
    font-size: 26px;
    text-align: center;
    color: white;
    border-bottom: solid 4px white;
    border-right: solid 4px white;
}
.eventdate_secondary {
    font-family: calibri;
    font-size: 26px;
    text-align: center;
    color: white;
    border-bottom: solid 4px white;
}
/*
//Hide the scrollbar
::-webkit-scrollbar { 
    display: none; 
}
*/
"""