template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Neuvotteluhuoneet</title>
    <meta http-equiv="refresh" content="120" >
    <link rel="stylesheet" href="./stylesheet.css"/>
</head>
<body>
    <script src="./dist/jquery-3.3.1.min.js"></script>
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
