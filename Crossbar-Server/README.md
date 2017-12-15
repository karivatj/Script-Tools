# Crossbar-Server

Crossbar.io implementation using Python sa backend solution and HTML/Javascript at the Frontend

All Python application code is in `/.py`. The backend is called from JavaScript, which is in `/web/index.html`.
#Remote Procedure Calls that can be used to get up-to-date data from different sources
com.testlab.haltian_location
com.testlab.withings_energy
com.testlab.withings_activity
com.testlab.withings_sleep
com.testlab.withings_bloodpressure
com.testlab.withings_bodytemperature
com.testlab.withings_average_heartrate

#Subscribable themes which serve data when new delta is received
com.testlab.haltian_location_update
com.testlab.withings_energy_update
com.testlab.withings_activity_update
com.testlab.withings_sleep_update
com.testlab.withings_bodytemp_update
com.testlab.withings_heartrate_update
com.testlab.withings_bloodpressure_update

#Dependencies:
python3
pypiwin32
paho-mqtt
python-dateutil
crossbarhttp3
requests-oauthlib

Microsoft Visual Studio Community edition
	-> Install Python workload + Native tools for development
	-> Install Desktop development workload and appropriate Win SDK for your distribution

Windows Env variables:
----------------------
LIB: 		C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.11.25503\lib\x64;C:\Program Files (x86)\Windows Kits\10\Lib\10.0.16299.0\um\x64;C:\Program Files (x86)\Windows Kits\10\Lib\10.0.16299.0\ucrt\x64
INCLUDE: 	C:\Program Files (x86)\Windows Kits\10\Include\10.0.16299.0\ucrt;C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.11.25503\include;C:\Program Files (x86)\Windows Kits\8.1\Include\shared;C:\Program Files (x86)\Windows Kits\10\Include\10.0.16299.0\um
PATH: 		C:\Users\Administrator.TESTLAB\AppData\Roaming\npm;C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.11.25503\bin\Hostx64\x64;C:\Program Files (x86)\Windows Kits\10\bin\10.0.16299.0\x64