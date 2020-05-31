import random
import time
import json
import string
import sys
import getopt


from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt

TBROKER = "localhost"
MQTTID  = "testcs"
TTOPIC  = "rpired/testcs/L/P"


def random_chars_string(l=5):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))


def on_connect(client, userdata, flags, rc):
    print("Connected to ", client._host, "port: ", client._port)
    print("Flags: ", flags, "returned code: ", rc)


if __name__ == "__main__":

    ICDELAY = 15        # inter content delay; default value 15 seconds
    CSIZE  = 100        # content size; default value 100 bytes
    try:
       opts, args = getopt.getopt(sys.argv[1:],"hd:s:",["delay=","size="])
    except getopt.GetoptError:
       print ('test.py -d <inter content delay> -s <content size>')
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print ('test.py -d <val1> -s <val2>')
          sys.exit()
       elif opt in ("-d", "--delay"):
          ICDELAY = arg
       elif opt in ("-s", "--size"):
          CSIZE = arg
    print ('inter content delay =', ICDELAY)
    print ('content size =', CSIZE)

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

    mqttc.loop_start()

    while True:

        devid = random.randint(0,9)             # Creating a random device
        rndcont = random_chars_string(CSIZE)    # Creating a random content

        payload = {
            "measurement": "ruuvis",
            "tags": {"devid": devid
            },
            "fields": { 
                "len": CSIZE,
                "cnt": rndcont
            }

        }
        jpaylaod = json.dumps(payload)

        print("content fileds: ", jpaylaod)

        mqttc.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)

        time.sleep(ICDELAY)

    mqttc.loop_stop()
