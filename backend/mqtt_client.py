import os
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")


def mqtt_configuration():
    return {
        "broker": MQTT_BROKER,
        "port": MQTT_PORT,
        "configured": bool(
            MQTT_BROKER and MQTT_USERNAME and MQTT_PASSWORD
        )
    }
