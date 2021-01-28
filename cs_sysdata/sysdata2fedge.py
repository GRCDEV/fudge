import random
import time
import json

import os
import paho.mqtt.client as mqtt

FREQ = 60
TBROKER = "localhost"
MQTTID  = "sysdata"
TTOPIC  = "rpired/sysdata/L/P"

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

    mqttc.loop_start()

    while True:

        CPU_Pct=round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2)
        # print("CPU Usage = " + CPU_Pct)

        tmp = os.popen('vcgencmd measure_temp').readlines()
        temp = float(tmp[0][5:-3])

        mem=os.popen('free -t -m').readlines()
        for line in mem:
            if "Total" in line:
                vals = line.split()
                # print ('Summary = ', vals)
                # print ('Total Memory = ' + vals[1] +' MB')
                # print ('Used Memory = ' + vals[2] +' MB')
                # print ('Free Memory = ' + vals[3] +' MB')

        payload = {
            "measurement": "sysdata",
            "tags": {
                "devid": "rpired"
            },
            "fields": {
                "cpu": CPU_Pct, 
                "temp": temp, 
                "umem": int(vals[2])
            }
        }
        jpaylaod = json.dumps(payload)

        print("Sysdata: ", jpaylaod)

        mqttc.publish(TTOPIC, payload=jpaylaod, qos=0, retain=False)

        time.sleep(FREQ)

    mqttc.loop_stop()
