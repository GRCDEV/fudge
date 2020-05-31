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
    return ''.join(random.choice(string.ascii_letters) for x in range(l))

def on_connect(client, userdata, flags, rc):
    print("Connected to ", client._host, "port: ", client._port)
    print("Flags: ", flags, "returned code: ", rc)


if __name__ == "__main__":

    ICDELAY = 15        # inter content delay; default value 15 seconds
    CSIZE  = 100        # content size; default value 100 bytes
    REPT   = 100        # number of messages sent
    try:
       opts, args = getopt.getopt(sys.argv[1:],"hd:s:r:",["delay=","size=","rep="])
    except getopt.GetoptError:
       print ('test.py -d <inter content delay> -s <content size> -r <number of repetitions')
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print ('test.py -d <val1> -s <val2> -r <val3>')
          sys.exit()
       elif opt in ("-d", "--delay"):
          ICDELAY = int(arg)
       elif opt in ("-s", "--size"):
          CSIZE = int(arg)
       elif opt in ("-r", "--rep"):
          REPT = int(arg)
    print ('inter content delay =', ICDELAY)
    print ('content size =', CSIZE)
    print ('number of repetitions =', REPT)

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

    for i in range(REPT):

        devid = random.randint(0,9)             # Creating a random device
        rndcont = random_chars_string(CSIZE)    # Creating a random content

        payload = {
            "measurement": "testcs",
            "tags": {"devid": devid
            },
            "fields": { 
                "tim": time.time(),
                "len": CSIZE,
                "cnt": rndcont
            }

        }
        jpaylaod = json.dumps(payload)

        print(i, "sending: ", jpaylaod)

        mqttc.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)

        time.sleep(ICDELAY)

    mqttc.loop_stop()
