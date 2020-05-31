import random
import time
import json

from influxdb import InfluxDBClient
from ruuvitag_sensor.ruuvitag import RuuviTag
import paho.mqtt.client as mqtt

# My ruuvi's MAC addresses:
RTAGS = ["F4:AF:92:D9:7C:3A", "C3:65:F4:40:E9:70", "C3:59:C9:93:81:DD"];

TBROKER = "localhost"
MQTTID  = "ruuvis"
TTOPIC  = "rpired/ruuvis/L/P"

def on_connect(client, userdata, flags, rc):
    print("Connected to ", client._host, "port: ", client._port)
    print("Flags: ", flags, "returned code: ", rc)


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
    print("Client connected to MQTT broker", TBROKER)

    sensors = []
    for s in RTAGS:
        sensors.append(RuuviTag(s))

    mqttc.loop_start()

    while True:

        for i in range(len(sensors)):
            # update state from the device
            try:
                state = sensors[i].update()
            except Exception as e:
                print("Something went wrong updating Ruuvi data... waiting 15 seconds and retrying")
                print(e.message, e.args)
                time.sleep(15)
                continue

            devid = RTAGS[i]
            payload = {
                "measurement": "ruuvis",
                "tags": {"devid": devid
                },
                "fields": state
            }
            jpaylaod = json.dumps(payload)

            print("Ruuvi data: ", jpaylaod)

            mqttc.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)

        time.sleep(15)

    mqttc.loop_stop()
