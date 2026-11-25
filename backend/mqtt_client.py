
import paho.mqtt.client as mqtt

# Configuración de Mosquitto local
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883

# Temas de comunicación
TOPIC_HUMIDITY = "smartirrigation/sensors/soil"
TOPIC_PUMP = "smartirrigation/pump"

client = None


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT conectado correctamente")

        client.subscribe(TOPIC_HUMIDITY)
        print(f"Escuchando: {TOPIC_HUMIDITY}")
    else:
        print(f"Error de conexión MQTT: {reason_code}")


def start_mqtt(on_message_callback):
    global client

    if client is not None:
        return

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_connect = on_connect
    client.on_message = on_message_callback

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()


def stop_mqtt():
    global client

    if client is not None:
        client.loop_stop()
        client.disconnect()
        client = None
        print("MQTT desconectado")
