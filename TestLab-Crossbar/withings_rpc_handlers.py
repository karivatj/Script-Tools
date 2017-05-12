#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#RPC Handler functions used by Withings node are described here
#

import json
from data_formatter import *

#dictionaries to hold measurement data
energy_data          = {}
activity_data        = {}
sleep_data           = {}
heartrate_data       = {}
bloodpressure_data   = {}
bodytemperature_data = {}

def withings_energy(data_format):
    data = {}
    print("withings_energy() called. Delivering payload")
    if data_format in "plotly": #return plotly compatible data
        for x in energy_data:
            data[x] = format_data_to_plotly(energy_data, x)
        return json.dumps(data)
    else:
        return json.dumps(energy_data)

def withings_activity(data_format):
    data = {}
    print("withings_activity() called. Delivering payload")
    if data_format in "plotly": #return plotly compatible data
        for x in activity_data:
            data[x] = format_data_to_plotly(activity_data, x)
        return json.dumps(data)
    if data_format in "intersystems": #return plotly compatible data
        for x in activity_data:
            data[x] = format_measurement_data_to_intersystems(activity_data, x)
        return json.dumps(data)
    else:
        return json.dumps(activity_data)

def withings_sleep(data_format):
    data = {}
    print("withings_sleep() called. Delivering payload")
    if data_format in "plotly": #return plotly compatible data
        for x in sleep_data:
            data[x] = format_data_to_plotly(sleep_data, x)
        return json.dumps(data)
    else:
        return json.dumps(sleep_data)

def withings_bloodpressure(data_format):
    data = {}
    print("withings_bloodpressure() called. Delivering payload")
    if data_format in "plotly": #return plotly compatible data
        for x in bloodpressure_data:
            data[x] = format_bloodpressure_data_to_plotly(bloodpressure_data, x)
        return json.dumps(data)
    elif data_format in "intersystems": #return intersystems compatible data via HTTP bridge
        for x in bloodpressure_data:
            data[x] = format_bloodpressure_data_to_intersystems(bloodpressure_data, x, "bloodPressure")
        return json.dumps(data)
    else:
        return json.dumps(bloodpressure_data)

def withings_bodytemperature(data_format):
    data = {}
    print("withings_bodytemperature() called. Delivering payload")
    if data_format in "plotly": #return plotly compatible data
        for x in bodytemperature_data:
            data[x] = format_measurement_data_to_plotly(bodytemperature_data, x)
        return json.dumps(data)
    elif data_format in "intersystems": #return intersystems compatible data via HTTP bridge
        for x in bodytemperature_data:
            data[x] = format_measurement_data_to_intersystems(bodytemperature_data, x, "bodyTemp")
        return json.dumps(data) 
    else:
        return json.dumps(bodytemperature_data)

def withings_average_heartrate(data_format):
    data = {}
    print("withings_average_heartrate() called. Delivering payload")
    if data_format in "plotly": #return plotly compatible data
        for x in heartrate_data:
            data[x] = format_measurement_data_to_plotly(heartrate_data, x)
        return json.dumps(data)
    elif data_format in "intersystems": #return intersystems compatible data via HTTP bridge
        for x in heartrate_data:
            data[x] = format_measurement_data_to_intersystems(heartrate_data, x, "avgHeartRate")
        return json.dumps(data)                 
    else:
        return json.dumps(heartrate_data)