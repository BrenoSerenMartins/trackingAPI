import logging
import paho.mqtt.client as mqtt
import json
import time
import random

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceMQTT:
    def __init__(self, client_id, mqtt_broker, topic):
        self.client_id = client_id
        self.mqtt_broker = mqtt_broker
        self.topic = topic
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Conectado ao broker MQTT com sucesso.")
        else:
            logger.error(f"Falha na conexão ao broker MQTT com código de resultado: {rc}")

    def simulate_device_location(self):
        try:
            result = self.client.connect(self.mqtt_broker, 1883, 60)
            if result == 0:
                logger.info("Conexão estabelecida com sucesso.")
                while True:
                    device_id = self.client_id
                    latitude = random.uniform(-90, 90)
                    longitude = random.uniform(-180, 180)
                    location_data = {
                        "device_code": device_id,
                        "latitude": latitude,
                        "longitude": longitude
                    }
                    self.client.publish(self.topic, json.dumps(location_data), qos=1)
                    logger.info(f"Dados de localização publicados: {location_data}")
                    time.sleep(3)  # Pode ser ajustado conforme necessário
            else:
                logger.error(f"Falha na conexão ao broker MQTT com código de resultado: {result}")
        except Exception as e:
            logger.error(f"Erro durante a conexão ao broker MQTT: {e}")


if __name__ == '__main__':
    # Configuração do Dispositivo MQTT
    client_id = "device123"
    mqtt_broker = "localhost"
    topic = "location_topic"

    device = DeviceMQTT(client_id, mqtt_broker, topic)
    logger.info("Iniciando simulação de dispositivo MQTT.")
    device.simulate_device_location()
