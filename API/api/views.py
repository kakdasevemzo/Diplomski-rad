from rest_framework import status
import paho.mqtt.client as mqtt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TelemetrySerializer
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from .models import Telemetry

from datetime import timedelta, datetime, timezone


# MQTT broker details
BROKER = 'broker.emqx.io'
PORT = 8083  # Use 8083 for WebSocket if needed
client = mqtt.Client(reconnect_on_failure=True, transport="websockets")
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

def initialize_mqtt_client():
    # Assigning callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    # Connect to the broker
    client.connect(BROKER, PORT, 60)
    
    # Start the network loop
    client.loop_start()

def publish_mqtt_message(topic, message):
    # Publish the message asynchronously
    result = client.publish(topic, message)
    # Optionally, handle publish results or errors here
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(f"Failed to publish message to topic {topic}")

def shutdown_mqtt_client():
    client.loop_stop()
    client.disconnect()

def parse_date_header(date_str):
    try:
        format_string = "%a, %d %b %Y %H:%M:%S %Z"

        # Parse the HTTP-date string to a datetime object
        datetime_obj = datetime.strptime(date_str, format_string)
        return datetime_obj
    except (ValueError, TypeError):
        return None

@api_view(['GET', 'PUT'])
def upload_telemetry(request):
    if request.method == 'GET':
        # Get query parameters
        duration = request.query_params.get('duration', '0')
        serial = request.query_params.get('serial', None)
        datetime_str = request.query_params.get('datetime', None)
        
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
        
        client_time_str = request.headers.get('Date')
        client_time = parse_date_header(client_time_str)
        
        if not client_time:
            return Response({'error': 'Invalid Date header'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the current server time in UTC
        server_time = datetime.now(timezone.utc)
        
        # Calculate the time offset (difference in seconds)
        time_offset = (server_time - client_time).total_seconds()
        initialize_mqtt_client()
        # Process each telemetry object in the list
        response_data = []
        telemetry_objects = []
        for telemetry_data in request.data:
            serializer = TelemetrySerializer(data=telemetry_data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                telemetry_object = Telemetry(**validated_data)  # Create the model instance
                telemetry_objects.append(telemetry_object)
                response_data.append(validated_data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Bulk create objects in the database
        if telemetry_objects:
            Telemetry.objects.bulk_create(telemetry_objects)

        # Publish MQTT messages asynchronously
        for telemetry_data in response_data:
            topic = f"telemetry/{telemetry_data.get('serial')}"
            message = f"{telemetry_data}"
            # Use an asynchronous task queue like Celery for publishing messages
            # async_publish_mqtt_message.delay(topic, message)
            # For now, we'll just call it synchronously for simplicity
            publish_mqtt_message(topic, message)
        shutdown_mqtt_client()
        return Response(response_data, status=status.HTTP_200_OK)
