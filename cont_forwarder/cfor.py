def read_from_db_messapp(topic, payload):

    pload = json.loads(payload)
    topic = topic.replace("request","response")

    results = clientIX.query("SELECT * FROM "+IXDB+".autogen."+pload["measurement"]+" where destination='"+pload["tags"]["destination"]+"'")
    if len(results) == 0: 
        mqttc.publish(topic, payload="NO DATA", qos=0, retain=False)
    else:   
        points = results.get_points()
        for point in points:
            payload = {
                "measurement": "messapp",
                "tags": {"sender": point['sender'], "time": point['time']},
                "fields": {"message": point['message']}
            }
            jpaylaod = json.dumps(payload)

            if JUST_FOR_DEBUG: print("read_from_db_messapp publishing: ", jpaylaod, " with topic ", topic)
            mqttc.publish(topic, payload=jpaylaod, qos=0, retain=False)
