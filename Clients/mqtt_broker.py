import logging
import paho.mqtt.client as mqtt
import json
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MQTTBroker:
    def __init__(self, broker_address, topic, api_url):
        self.broker = mqtt.Client()
        self.broker.on_message = self.on_message
        self.broker_address = broker_address
        self.topic = topic
        self.api_url = api_url

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        logger.info(f"Received message on topic '{msg.topic}': {payload}")

        # Send data to API
        try:
            response = requests.post(self.api_url, json=json.loads(payload))

            if response.status_code == 200:
                logger.info("Success")
            else:
                logger.error(f"Error: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")

    def run(self):
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker_address}...")
            self.broker.connect(self.broker_address, 1883, 60)
            logger.info(f"Subscribing to topic '{self.topic}'...")
            self.broker.subscribe(self.topic, qos=1)
            logger.info("MQTT Broker is running and waiting for messages.")
            self.broker.loop_forever()
        except KeyboardInterrupt:
            logger.info("Received KeyboardInterrupt. Cleaning up and exiting.")
            self.broker.disconnect()


if __name__ == '__main__':
    # Config MQTT BROKER
    broker_address = "localhost"
    topic = "location_topic"
    api_url = "http://localhost:5003/queue/add_device_location"

    broker = MQTTBroker(broker_address, topic, api_url)
    broker.run()
