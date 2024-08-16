import paho.mqtt.client as mqtt
import random

# Configuration
BROKER = "ws-reader.v2.sondehub.org"
PORT = 80
CLIENT_ID = "SondeHub-Tracker-" + str(int(random.random() * 10000000000))
TOPIC_PREFIX = "sondes-new/#"  # Default topic to subscribe to

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC_PREFIX)
    print(f"Subscribed to {TOPIC_PREFIX}")

# Callback when a message is received from the broker
def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

# Callback when the connection to the broker is lost
def on_disconnect(client, userdata, rc,A,B):
    if rc != 0:
        print(f"Unexpected disconnection. Code: {rc}")
    else:
        print("Disconnected successfully")

# Create a new MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
client.ws_set_options(path="/")
# Optionally set WebSocket options if required by the broker
# client.ws_set_options(path="/", headers={})  # Adjust path and headers if needed

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to the MQTT broker
try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    while True:
        pass  # Keep the script running

except KeyboardInterrupt:
    print("Disconnecting...")
    client.loop_stop()
    client.disconnect()
