import random
import time
import json

import os
import paho.mqtt.client as mqtt

FREQ = 60
TBROKER = "localhost"
MQTTID  = "lbrokdata"
TTOPIC  = "rpired/lbrokdata/L/P"

cli_con = -1
rec_15m = -1
sen_15m = -1

def on_connect(client, userdata, flags, rc):
    print("Connected to ", client._host, "port: ", client._port)
    print("Flags: ", flags, "returned code: ", rc)
    client.subscribe("$SYS/broker/clients/connected")
    client.subscribe("$SYS/broker/load/messages/received/15min")
    client.subscribe("$SYS/broker/load/messages/sent/15min")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    themsg   = json.loads(msg.payload.decode("utf-8"))
    print(msg.topic)
    print(msg.payload)
    print(themsg)
    if ("clients/connected" in msg.topic):
        cli_con = int(themsg)
    if ("received/15min" in msg.topic):
        rec_15m = int(themsg)
    if ("sent/15min" in msg.topic):
        sen_15m = int(themsg)

if __name__ == "__main__":

    try:
        mqttc = mqtt.Client(client_id=MQTTID, clean_session=True)
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.username_pw_set(None, password=None)
        mqttc.connect(TBROKER, port=1883, keepalive=60)
    except Exception as e:
        print("Something went wrong connecting to the MQTT broker")
        print(e)
        sys.exit(2)
    print("Client connected to MQTT broker", TBROKER)

    mqttc.loop_start()

    while True:

        payload = {
            "measurement": "lbrokdata",
            "tags": {
                "devid": "rpired"
            },
            "fields": {
                "cli_con": cli_con, 
                "rec_15m": rec_15m, 
                "sen_15m": sen_15m
            }
        }
        jpaylaod = json.dumps(payload)

        print("lbrokdata: ", jpaylaod)

        mqttc.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)

        time.sleep(FREQ)

    mqttc.loop_stop()
