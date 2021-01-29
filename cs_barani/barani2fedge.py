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
TTOPIC  = "rpired/barani/L/P"

# The callback for when the client receives a CONNACK response from the server.
def on_connectFUDGE(client, userdata, flags, rc):
	print("Flags: ", flags, "returned code: ", rc)

# The callback for when the client receives a CONNACK response from the server.
def on_connectTTN(client, userdata, flags, rc):
	client.subscribe(TTN_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	global mqttc
	global TTOPIC

	themsg   = json.loads(msg.payload.decode("utf-8"))
#	print(themsg)
	
# {'app_id': 'barani_ws', 'dev_id': 'meteohelix049', 'hardware_serial': '0004A30B00F2CE16', 'port': 1, 'counter': 1548, 'payload_raw': 'by4BBbtC2DoBAP8=', 'payload_fields': {'Battery': 4.15, 'Humidity': 44.2, 'Irr_max': 60, 'Irradiation': 58, 'Pressure': 101655, 'Rain': 0, 'Rain min time': 255, 'T_max': 20.9, 'T_min': 20.7, 'Temperature': 20.8, 'Type': 1}, 'metadata': {'time': '2021-01-29T09:30:51.438054513Z', 'frequency': 868.3, 'modulation': 'LORA', 'data_rate': 'SF12BW125', 'airtime': 1482752000, 'coding_rate': '4/5', 'gateways': [{'gtw_id': 'eui-b827ebfffe7fe28a', 'timestamp': 3561139820, 'time': '2021-01-29T09:30:51.410093Z', 'channel': 1, 'rssi': -73, 'snr': 5.2, 'rf_chain': 0, 'latitude': 39.48262, 'longitude': -0.34657, 'altitude': 10}, {'gtw_id': 'eui-b827ebfffe336296', 'timestamp': 3453459404, 'time': '', 'channel': 1, 'rssi': -49, 'snr': 6.8, 'rf_chain': 0}]}}


	dvid = themsg["dev_id"]
	humi = themsg["payload_fields"]["Humidity"]
	irra = themsg["payload_fields"]["Irradiation"]
	pres = themsg["payload_fields"]["Pressure"]
	temp = themsg["payload_fields"]["Temperature"]

	payload = {
		"measurement": "barani",
		"tags": {
			"devid": dvid
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

	mqttc.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)


if __name__ == "__main__":

	try:
		mqttc = mqtt.Client()
		mqttc.on_connect = on_connectFUDGE
		mqttc.username_pw_set(None, password=None)
		mqttc.connect(TBROKER, port=1883, keepalive=60)
        mqttc.loop_start()
	except Exception as e:
		print("Something went wrong connecting to the MQTT broker")
		print(e)
		sys.exit(2)
    finally:
    	print("Client connected to local broker")

	try:
		clientTT = mqtt.Client()
		clientTT.on_connect = on_connectTTN
		clientTT.on_message = on_message
		clientTT.username_pw_set(TTN_USER, password=TTN_PASS)
		clientTT.connect(TTN_BROKER, 1883, 60)
        clientTT.loop_start()
	except Exception as e:
		print("Something went wrong connecting to TTN_BROKER")
		print(e.message, e.args)
        sys.exit(2)
	finally:
		print("Client connected to TTN_BROKER: ", TTN_BROKER)


