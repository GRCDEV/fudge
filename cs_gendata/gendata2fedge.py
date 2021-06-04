import random
import time
import json

import paho.mqtt.client as mqtt

BROKER  = "localhost"
BUSER   = "fudgeuser"
BPAWD   = "fudgepass"
MQTTID  = "gendata"

TTOPIC  = "rpired/sysdata/L/P"
FREQ = 60


def gen_rand_string(len=10):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = len))    

def on_connect(client, userdata, flags, rc):
    print("Connected to ", client._host, "port: ", client._port)
    print("Flags: ", flags, "returned code: ", rc)


if __name__ == "__main__":

    try:
        mqttc = mqtt.Client(client_id=MQTTID, clean_session=True)
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
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
            "measurement": "gendata",
            "tags": {
                "devid": "rpired"
            },
            "fields": {
                "rndstring": CPU_Pct, 
                "rndnum": temp, 
            }
        }
        jpaylaod = json.dumps(payload)

        print("Sysdata: ", jpaylaod)

        mqttc.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)

        time.sleep(FREQ)

    mqttc.loop_stop()
