from flask import Flask, redirect, url_for, render_template, request, session

from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt



# imports
import json
import sys
import time
import hashlib
from datetime import datetime, timezone, timedelta

IXSERVER = "localhost"
IXDB     = "messapp"
IXUSER   = None
IXPASS   = None

clientIX = None
mqttc = None

TBROKER = "localhost"
MQTTID  = "messapp"

inmessages = [] 

def on_connect(client, userdata, flags, rc):
    if rc > 0:
        print("[ERROR:on_connect]: %d - calling on_connect()\n" % (rc))
        sys.exit(2)
    else:
        client.subscribe('rpired/messapp/L/X/response', qos=0)

def on_message(mqttc, userdata, msg):
    global inmessages

    print("[DEBUG:on_message] Received: '%s', topic: '%s' (qos=%d)\n" % (msg.payload, msg.topic, msg.qos))

    pload = json.loads(msg.payload)
    inmessages.append(pload)


app = Flask(__name__)
app.secret_key = "socciacheduemaroni"
app.permanent_session_lifetime = timedelta(minutes=60)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    global IXDB

    if request.method == "POST":

        usr  = request.form["usr"]
        # computing hash code of the inserted password
        ppwd = request.form["pwd"].encode('utf-8')
        hpwd = hashlib.sha224(ppwd).hexdigest()

        # check if user credentials are in database
        results = clientIX.query('SELECT * FROM '+IXDB+'.autogen.logins')
        points = results.get_points(tags={'uname':request.form["usr"]})
        try: 
            point = next(points)
            uname = point["uname"]
            upass = point["upass"]
        except StopIteration:
            uname = None
            upass = None

        if uname == usr:
            if upass == hpwd:
                session.permanent = True
                session["user"] = usr
                return redirect("sendmsg")
            else: 
                return render_template("login.html", feedback="Wrong password.")
        else:
            return render_template("login.html", feedback="Wrong username, try again or register.")

    else:
        if "user" in session:
            return redirect("sendmsg")

        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    global IXDB
    global clientIX

    if request.method == "POST":

        # checking if form was fully filled in
        req = request.form
        missing = list()
        for k, v in req.items():
            if v == "":
                missing.append(k)
        if missing:
            feedback = f"Missing fields for {', '.join(missing)}"
            return render_template("register.html", feedback=feedback)

        # check if user credentials "username" are alrady in the database
        uname = request.form["username"]
        results = clientIX.query("SELECT * FROM "+IXDB+".autogen.logins where uname='"+uname+"'")
        if len(results) == 0: # username is not already registered
            email = request.form["email"]
            # storing hash code of the inserted password
            upass = request.form["password"].encode('utf-8')
            hpass = hashlib.sha224(upass).hexdigest()
            now_time = datetime.now(timezone.utc).astimezone()
            udata = [{
                "measurement": "logins",
                "tags": {"uname": uname},
                "time": now_time.isoformat(),
                "fields": {"upass": hpass, "email": email}
            }]
            print("DEBUG: ",  udata)

            try:
                clientIX.write_points(udata, database=IXDB, protocol='json')
            except Exception as e:
                print("DEBUG: Something went wrong during 'write_points' InfluxDB DB")
                print(e)

            # setting session active
            session["user"] = request.form["username"]
            return redirect("sendmsg")
        else:
            return render_template("register.html", feedback="User already registered")
    else:
        return render_template("register.html")

@app.route("/sendmsg", methods=["GET", "POST"])
def sendmsg():
    global mqttc

    if not "user" in session:
        return redirect("login")

    if request.method == "POST":

        req = request.form

        missing = list()
        for k, v in req.items():
            if v == "":
                missing.append(k)
        if missing:
            feedback = f"Missing values for {', '.join(missing)}"
            return render_template("sendmsg.html", feedback=feedback, uname=session["user"])

        destination = request.form["destination"]
        message = request.form["message"]
        mqttc.loop_start()
        payload = {
            "measurement": "messapp",
            "tags": {"sender": session["user"], "destination": destination},
            "fields": {"message": message}
        }
        jpaylaod = json.dumps(payload)

        print("messapp data: ", jpaylaod)

        mqttc.publish('rpired/messapp/L/P', payload=jpaylaod, qos=0, retain=False)
        mqttc.loop_stop()

        return redirect(request.url)

    return render_template("sendmsg.html", uname=session["user"])

@app.route("/getmsg", methods=["GET", "POST"])
def getmsg():
    global mqttc

    if not "user" in session:
        return redirect("login")

    if request.method == "POST":

        payload = {
            "measurement": "messapp",
            "tags": {"sender": "", "destination": session["user"]},
            "fields": {"message": ""}
        }
        jpaylaod = json.dumps(payload)

        mqttc.loop_start()
        mqttc.publish('rpired/messapp/L/X/request', payload=jpaylaod, qos=0, retain=False)
        time.sleep(5) # giving time for messages to come
        print("inmessages", inmessages)
        mqttc.loop_stop()

        return render_template("getmsg.html", uname=session["user"], inmessages = inmessages)
    else: 
        return render_template("getmsg.html", uname=session["user"])

@app.route("/logout")
def logout():
    if not "user" in session:
        return redirect("login")
    else:
        user = session["user"]
        session.pop("user", None)
        return render_template("logout.html", uname=user)


if __name__ == "__main__":

    # used to store users data
    try:
        clientIX = InfluxDBClient(host=IXSERVER, port=8086, username=IXUSER, password=IXPASS, database=IXDB)
    except Exception as e:
        print("Something went wrong connecting to InfluxDB server")
        print(e)
        sys.exit(2)
    print("Client connected to InfluxDB server")
    try:
        clientIX.create_database(IXDB)
    except Exception as e:
        print("Something went wrong creating InfluxDB DB")
        print(e)
        sys.exit(2)
    print("Created InfluxDB DB: ", IXDB)


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


    # results = clientIX.query('SELECT * FROM '+IXDB+'."autogen"."logins"')
    # print(results.raw)

    app.run(host='0.0.0.0', port=5000, debug=True)




