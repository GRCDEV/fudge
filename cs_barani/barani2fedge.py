import base64
import json
import os
import random
import struct
import sys
import time

import paho.mqtt.client as mqtt

TTN_BROKER = "eu.thethings.network"
TTN_TOPIC  = "+/devices/+/up"
TTN_USER   = "barani_ws"   # the Application ID
TTN_PASS   = "ttn-account-v2.VL4XZUiF9gIsrJDiCWZU6ZmnW_SM3LIf4Jx65KMxQWQ" # the Application Access Key

FREQ = 60
TBROKER = "localhost"
MQTTID  = "barani"
TTOPIC  = "rpired/barani/L/P"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	client.subscribe(TTN_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	themsg   = json.loads(msg.payload.decode("utf-8"))
    print(themsg)
	
	fclient  = userdata # fudge client

# {
#   "Battery": 4.15,
#   "Humidity": 44.2,
#   "Irr_max": 0,
#   "Irradiation": 0,
#   "Pressure": 101575,
#   "Rain": 0,
#   "Rain min time": 255,
#   "T_max": 24,
#   "T_min": 24,
#   "Temperature": 24,
#   "Type": 1
# }
	humi = themsg["Humidity"]
	irra = themsg["Irradiation"]
	pres = themsg["Pressure"]
	temp = themsg["Temperature"]

	payload = {
		"measurement": "barani",
		"tags": {
			"devid": "barani_ws"
		},
		"fields": {
			"humi": humi,
			"irra": irra,
			"pres": pres, 
			"temp": temp, 
		}
	}
	jpaylaod = json.dumps(payload)

	print("barani data: ", jpaylaod)

	fclient.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)



if __name__ == "__main__":

	try:
		mqttc = mqtt.Client(client_id=MQTTID, clean_session=True)
		mqttc.on_connect = on_connect
		mqttc.username_pw_set(None, password=None)
		mqttc.connect(TBROKER, port=1883, keepalive=60)
	except Exception as e:
		print("Something went wrong connecting to the MQTT broker")
		print(e)
		sys.exit(2)
	print("Client connected to local broker")

	try:
		clientTT = mqtt.Client()
		clientTT.on_connect = on_connect
		clientTT.on_message = on_message
		clientTT.user_data_set(mqttc)    # passing fudge client to callback
		clientTT.username_pw_set(TTN_USER, password=TTN_PASS)
		clientTT.connect(TTN_BROKER, 1883, 60)
	except Exception as e:
		print("Something went wrong connecting to TTN_BROKER")
		print(e.message, e.args)
	finally:
		print("Client connected to TTN_BROKER: ", TTN_BROKER)


	clientTT.loop_forever()
