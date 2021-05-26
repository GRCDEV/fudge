# FUDGE: a frugal edge node for IoT deployment in remote areas

The growing connection between the Internet of Things (IoT) and Artificial Intelligence (AI) poses many challenges that require novel approaches and even a rethinking of the entire communication and processing architecture to meet new requirements for latency, reliability, power consumption and resource usage. Edge computing  is a promising approach to meet these challenges that can also be beneficial in delivering advanced AI-based IoT solutions in areas where connectivity is scarce and resources are generally limited.

With FUDGE, we introduce an edge/fog generic architecture to allow the adoption of edge solutions in IoT deployments in poorly connected and resource limited scenarios. To this end, we integrate, using micro-services, an MQTT based system that can collect ingress data, handle their persistency, and coordinate data integration with the cloud using a specific service called aggregator.  The edge stations have a dedicated channel with the aggregator based on LoRa to enable long-range transmissions with low power consumption. Some details of the implementation aspects are described along with some preliminary results. Initial testing of the architecture indicates that it is flexible and robust enough to become an alternative for the deployment of advanced IoT services in resource-constrained contexts.

More details here: https://dl.acm.org/doi/10.1145/3410670.3410857

## Installing a basic FUDGE
We use as a reference a Raspberry Pi 3B.

The basic installation consists of:

* [mosquitto broker](https://mosquitto.org)
    - we are currently using mosquitto version 1.5.7
* Python3 (typically already available in the current raspberry distibution)
    - [paho-mqtt](https://pypi.org/project/paho-mqtt/) library has to be installed
* [Docker](https://www.raspberrypi.org/blog/docker-comes-to-raspberry-pi/)
    - curl -sSL https://get.docker.com | sh
    - sudo usermod -aG docker pi

The basic components to be executed are:

* Mosquitto broker
    - check if active: $ systemctl status mosquitto
* influxDB
    > https://songrgg.github.io/operation/influxdb-command-cheatsheet/
    - $ docker run -d -p 8086:8086  -v $PWD:/var/lib/influxdb --name=influxdb influxdb
    * restart: $ docker start influxdb
    * access with: $ docker exec -it influxdb influx        
* Grafana
    > https://hackmd.io/2Ou5NfDHQfetCvhsWKJQMw#Step-2-processing-and-visualizing-data
    - $ docker run -d --name=grafana -p 3000:3000 grafana/grafana-arm32v7-linux:dev-musl 
    * restart: $ docker start grafana
    - Access from browser: 
        - http://158.42.55.3:3000/login
* Execute the persistency manager
    * $ python3 pman.py

