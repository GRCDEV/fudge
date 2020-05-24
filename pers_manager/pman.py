import argparse
import logging
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

TBROKER = "localhost"
MQTTID  = "pmanager"
TTOPIC  = "rpired/#"

# Debugging related stuff
DEBUG_MSG_ON = False
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] [%(threadName)-10s%(message)s',)

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

            print("read_from_db_messapp publishing: ", jpaylaod, " with topic ", topic)
            mqttc.publish(topic, payload=jpaylaod, qos=0, retain=False)


def create_json_data(topic, payload):
    print(topic, payload)
    pload = json.loads(payload)

    print(pload)

    now_time = datetime.now(timezone.utc).astimezone()

    return [{
        "measurement": pload["measurement"],
        "tags": pload["tags"],
        "time": now_time.isoformat(),
        "fields": pload["fields"]
    }]


def on_connect(mqttc, userdata, flags, rc):
    logging.debug("[DEBUG:on_connect] Connected to %s : %d\n" % (mqttc._host, mqttc._port))
    if rc > 0:
        sys.stderr.write("[ERROR:on_connect]: %d - calling on_connect()\n" % rc)
        sys.exit(2)
    else:
        mqttc.subscribe(TTOPIC, qos=0)

def on_subscribe(mqttc, userdata, mid, granted_qos):
    if DEBUG_MSG_ON: sys.stderr.write("[DEBUG:on_subscribe] Subscribed: "+str(mid)+" "+str(granted_qos)+"\n")

def on_message(mqttc, userdata, msg):
    if DEBUG_MSG_ON: sys.stderr.write("[DEBUG:on_message] Received from %s: '%s', topic: '%s' (qos=%d)\n" % (fb, msg.payload, msg.topic, msg.qos))

    top = msg.topic.split('/')
    if (top[3]=='P'):    # Checking if data must be made persistent
        jrecord = create_json_data(msg.topic, msg.payload)
        print("PERSISTING :) ", jrecord)
        try:
            clientIX.write_points(jrecord, database=IXDB, protocol='json')
        except Exception as e:
            print("Something went wrong during 'write_points' InfluxDB DB")
            print(e)
    elif (top[3]=='X') and (top[4]=='request'):
        read_from_db_messapp(msg.topic, msg.payload)
    else:
        pass # nothing to do

def on_publish(mqttc, userdata, mid):
    if DEBUG_MSG_ON: sys.stderr.write("[DEBUG:on_publish] Sent messageid '%d'\n" % mid)



if __name__ == "__main__":

    logging.basicConfig(format='%(levelname)s:%(funcName)s:%(lineno)d:%(message)s', level=logging.DEBUG)

    # Conecting to the InfluxDB server
    try:
        clientIX = InfluxDBClient(host=IXSERVER, port=8086, username=IXUSER, password=IXPASS, database=IXDB)
    except Exception as e:
        print("Something went wrong connecting to InfluxDB server")
        print(e.message, e.args)
        sys.exit(2)
    print("Client connected to InfluxDB server")

    # Creating InfluxDB DB
    try:
        clientIX.create_database(IXDB)
    except Exception as e:
        print("Something went wrong creating InfluxDB DB")
        print(e.message, e.args)
        sys.exit(2)
    print("Created InfluxDB DB: ", IXDB)

    mqttc = mqtt.Client(client_id=MQTTID, clean_session=True, userdata=None)
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe

    # Connect to the MQTT brokers
    mqttc.username_pw_set(None, password=None)
    try:
        print("Connecting to: ", TBROKER)
        mqttc.connect(TBROKER, 1883, keepalive=60)
    except socket.error as serr:
        sys.stderr.write("[ERROR] %s\n" % serr)
        sys.exit(2)

    mqttc.loop_forever()
