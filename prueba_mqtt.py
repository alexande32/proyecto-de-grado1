import json
import paho.mqtt.client as mqtt

cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

cliente.connect("127.0.0.1", 1883, 60)

mensaje = {
    "humidity": 45.5,
    "soil_raw": 1850
}

resultado = cliente.publish(
    "smartirrigation/sensors/soil",
    json.dumps(mensaje)
)

resultado.wait_for_publish()

print("Mensaje enviado:", json.dumps(mensaje))

cliente.disconnect()