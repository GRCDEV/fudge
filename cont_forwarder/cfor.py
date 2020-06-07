import argparse
import json 
import sys
import socket
import threading
import time

import csv
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from influxdb import InfluxDBClient

IXSERVER = "localhost"
IXDB     = "fudgedb"
IXUSER   = None
IXPASS   = None

def read_from_db_messapp(topic, payload):

    pload = json.loads(payload)
    topic = topic.replace("request","response")

    results = clientIX.query("SELECT * FROM "+IXDB+".autogen."+pload["measurement"]+" where destination='"+pload["tags"]["destination"]+"'")
    if len(results) == 0: 
        mqttc.publish(topic, payload="NO DATA", qos=0, retain=False)
    else:   
        points = results.get_points()
        for point in points:
            payload = {
                "measurement": "messapp",
                "tags": {"sender": point['sender'], "time": point['time']},
                "fields": {"message": point['message']}
            }
            jpaylaod = json.dumps(payload)

            if JUST_FOR_DEBUG: print("read_from_db_messapp publishing: ", jpaylaod, " with topic ", topic)
            mqttc.publish(topic, payload=jpaylaod, qos=0, retain=False)



if __name__ == "__main__":

    # Conecting to the InfluxDB server
    try:
        clientIX = InfluxDBClient(host=IXSERVER, port=8086, username=IXUSER, password=IXPASS, database=IXDB)
    except Exception as e:
        sys.stderr.write("[ERROR] Something went wrong connecting to InfluxDB server")
        print(e.message, e.args)
        sys.exit(2)
    print("[INFO:main] Client connected to InfluxDB server")

    # Accessing the InfluxDB DB
    try:
        clientIX.switch_database(IXDB)
    except Exception as e:
        sys.stderr.write("[ERROR] Something went wrong setting the InfluxDB DB")
        print(e.message, e.args)
        sys.exit(2)
    print("[INFO:main] Set InfluxDB DB: ", IXDB)


    msrts = clientIX.get_list_measurements()
    for m in msrts:
        print(m["name"])
        if m["name"]=="testcs":
            rs = clientIX.query("SELECT * from "+m["name"])
            rsp = list(rs.get_points(tags={"scope": "G"}))
            for k in rsp:
                print(k)



