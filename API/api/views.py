from rest_framework import status
import paho.mqtt.client as mqtt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TelemetrySerializer
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from .models import Telemetry
from datetime import timedelta


# MQTT broker details
BROKER = 'broker.emqx.io'
PORT = 8083  # Use 8083 for WebSocket if needed

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published with id: {mid}")

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT Broker")

# Function to publish MQTT messages
def publish_mqtt_message(topic, message):
    client = mqtt.Client()
    
    # Assigning callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    # Connect to the broker
    client.connect(BROKER, PORT, 60)
    
    # Start the network loop
    client.loop_start()

    # Publish the message
    result = client.publish(topic, message)
    
    # Wait for the publish to complete
    result.wait_for_publish()

    # Stop the loop and disconnect
    client.loop_stop()
    client.disconnect()

@api_view(['GET', 'PUT'])
def upload_telemetry(request):
    if request.method == 'GET':
        # Get query parameters
        duration = request.query_params.get('duration', '0')
        serial = request.query_params.get('serial')
        datetime_str = request.query_params.get('datetime', now().isoformat())
        
        try:
            end_time = parse_datetime(datetime_str)
            if end_time is None:
                return Response({'error': 'Invalid datetime format'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid datetime format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate start time based on duration
        duration_mapping = {
            '15s': timedelta(seconds=15),
            '1m': timedelta(minutes=1),
            '30m': timedelta(minutes=30),
            '1h': timedelta(hours=1),
            '3h': timedelta(hours=3),
            '6h': timedelta(hours=6),
            '1d': timedelta(days=1),
            '3d': timedelta(days=3),
        }
        if duration in duration_mapping:
            start_time = end_time - duration_mapping[duration]
        else:
            start_time = None

        # Filter telemetry data
        if serial:
            if start_time:
                telemetry_data = Telemetry.objects.filter(serial=serial, datetime__range=(start_time, end_time))
            else:
                telemetry_data = Telemetry.objects.filter(serial=serial, datetime__lte=end_time)
        else:
            if start_time:
                telemetry_data = Telemetry.objects.filter(datetime__range=(start_time, end_time))
            else:
                telemetry_data = Telemetry.objects.filter(datetime__lte=end_time)
        
        # Serialize and organize data
        telemetry_dict = {}
        for telemetry in telemetry_data:
            serial = telemetry.serial
            datetime_str = telemetry.datetime.isoformat()
            if serial not in telemetry_dict:
                telemetry_dict[serial] = {}
            telemetry_dict[serial][datetime_str] = TelemetrySerializer(telemetry).data
        
        return Response(telemetry_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        # Ensure the request data is a list
        if not isinstance(request.data, list):
            return Response({'error': 'Expected a list of telemetry objects'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process each telemetry object in the list
        response_data = []
        for telemetry_data in request.data:
            serializer = TelemetrySerializer(data=telemetry_data)
            if serializer.is_valid():
                serializer.save()
                response_data.append(serializer.data)
                topic = f"telemetry/{telemetry.get('serial')}"
                message = f"Telemetry data received: {telemetry}"
                publish_mqtt_message(topic, message)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status.HTTP_200_OK)
