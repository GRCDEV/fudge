import random
import time
import json
import string
import sys

import paho.mqtt.client as mqtt

BROKER  = "localhost"
BUSER   = "fudgeuser"
BPAWD   = "fudgepass"

TDEVICE = "tdevice"
MEASRMT = "gendata"

TTOPIC  = TDEVICE+"/"+MEASRMT+"/L/P"
FREQ    = 60
TXTSIZE = 5


def gen_rand_string(len=10):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = len))    

def on_connect(client, userdata, flags, rc):
    print("Connected to ", client._host, "port: ", client._port)
    print("Flags: ", flags, "returned code: ", rc)


if __name__ == "__main__":

    try:
        mqttc = mqtt.Client(client_id=MEASRMT, clean_session=True)
        mqttc.on_connect = on_connect
        mqttc.username_pw_set(BUSER, BPAWD)
        mqttc.connect(BROKER, port=1883, keepalive=60)
    except Exception as e:
        print("Something went wrong connecting to the MQTT broker")
        print(e)
        sys.exit(2)
    print("Client connected to MQTT broker", BROKER)

    mqttc.loop_start()

    while True:


        payload = {
            "measurement": MEASRMT,
            "tags": {
                "devid": TDEVICE
            },
            "fields": {
                "rndstring": gen_rand_string(TXTSIZE), 
                "rndnum": random.randint(0,1000) 
            }
        }
        jpaylaod = json.dumps(payload)

        print("gendata: ", jpaylaod)

        mqttc.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)

        time.sleep(FREQ)

    mqttc.loop_stop()
