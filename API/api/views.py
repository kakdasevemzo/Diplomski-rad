from rest_framework import status
import paho.mqtt.client as mqtt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TelemetrySerializer
from django.utils.dateparse import parse_datetime
from .models import Telemetry
from django.http import JsonResponse
from zoneinfo import ZoneInfo

from datetime import timedelta, datetime, timezone


# MQTT broker details
BROKER = 'broker.emqx.io'
PORT = 8084  # Port for WebSocket Secure (WSS)
WEBSOCKET_PATH = '/mqtt'  # WebSocket path

# Generate a client ID similar to the JavaScript frontend
import random
clientID = "SondeHub-Tracker-" + str(random.randint(0, 10000000000))

# Create an MQTT client instance with WebSocket transport
client = mqtt.Client(client_id=clientID, transport="websockets")

# Set WebSocket options including path
client.ws_set_options(path=WEBSOCKET_PATH)

client.tls_set()
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
    print(f'publishing to topic: {topic}')
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
        client_time = datetime_obj.replace(tzinfo=timezone.utc)
        return client_time
    except (ValueError, TypeError):
        return None
    
def round_to_nearest_second(dt):
    # Calculate the number of seconds to add or subtract
    delta = timedelta(microseconds=dt.microsecond)
    if delta >= timedelta(microseconds=500000):  # 0.5 seconds
        return dt + timedelta(seconds=1) - timedelta(microseconds=dt.microsecond)
    else:
        return dt - timedelta(microseconds=dt.microsecond)


@api_view(['GET', 'PUT'])
def upload_telemetry(request):
    if request.method == 'GET':
        print(f'Started GET!!!!!!!')
        # Get query parameters
        duration = request.query_params.get('duration', None)
        serial = request.query_params.get('serial', None)
        datetime_str = request.query_params.get('datetime', None)
        print('datetime_str: ', datetime_str)
        server_time = datetime.now(timezone.utc)
        if duration == '0' or duration is None:
            if not serial or not datetime_str:
                return JsonResponse({'error': 'Both serial and datetime parameters are required when duration is 0 or None'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Parse the datetime string
                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                if datetime_obj is None:
                    raise ValueError("Invalid datetime format")
            except ValueError:
                return JsonResponse({'error': 'Invalid datetime format'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch the telemetry data for the given serial and datetime
            original_datetime = datetime_obj  # Assuming datetime_obj is your input datetime
            original_datetime = original_datetime.replace(tzinfo=ZoneInfo('UTC'))
            print(f'ORIGINAL DATETIME: {original_datetime}')

            rounded_date = round_to_nearest_second(original_datetime)
            print(f'ROUNDED DATETIME: {original_datetime}')
            # Step 2: Define the time range (2 seconds before and after)
            start_datetime = rounded_date - timedelta(microseconds=500000)
            end_datetime = rounded_date + timedelta(microseconds=500000)
            print(f"This is start_datetime and end_datetime: {start_datetime}, {end_datetime}")
            telemetry_data = Telemetry.objects.filter(serial=serial, datetime__range=(start_datetime, end_datetime))

            uploaders = []

            for telemetry in telemetry_data:
                uploader_info = {}
                
                # Extract uploader_callsign, frequency, and snr if they exist
                if telemetry.uploader_callsign:
                    uploader_info["uploader_callsign"] = telemetry.uploader_callsign
                
                if telemetry.frequency:
                    uploader_info["frequency"] = telemetry.frequency
                
                if telemetry.snr:
                    uploader_info["snr"] = telemetry.snr

                if telemetry.rssi:
                    uploader_info["rssi"] = telemetry.rssi
                
                # Only add the dictionary to the list if it has at least one key-value pair
                if uploader_info:
                    uploaders.append(uploader_info)

            if telemetry_data.exists():
                first_entry = telemetry_data.first()
                uploader_position = str(first_entry.uploader_position[0]) + ',' + str(first_entry.uploader_position[1])
                position = str(first_entry.lat) + ',' + str(first_entry.lon)
                uploader_altitude = str(first_entry.uploader_position[2])
                # Construct the response dictionary
                response = {
                    serial: {
                        datetime_str: {
                            "software_name": first_entry.software_name,
                            "software_version": first_entry.software_version,
                            "uploader_callsign": first_entry.uploader_callsign,
                            "uploader_position": uploader_position,
                            "uploader_antenna": first_entry.uploader_antenna,
                            "time_received": first_entry.time_received.isoformat(),
                            "datetime": first_entry.datetime.isoformat(),
                            "manufacturer": first_entry.manufacturer,
                            "type": first_entry.type,
                            "serial": first_entry.serial,
                            "subtype": first_entry.subtype,
                            "frame": first_entry.frame,
                            "lat": first_entry.lat,
                            "lon": first_entry.lon,
                            "alt": first_entry.alt,
                            "temp": first_entry.temp,
                            "humidity": first_entry.humidity,
                            "vel_v": first_entry.vel_v,
                            "vel_h": first_entry.vel_h,
                            "heading": first_entry.heading,
                            "sats": first_entry.sats,
                            "batt": first_entry.batt,
                            "frequency": first_entry.frequency,
                            "burst_timer": first_entry.burst_timer,
                            "snr": first_entry.snr,
                            "tx_frequency": first_entry.tx_frequency,
                            "user-agent" : first_entry.user_agent,
                            "position": position,
                            "uploader_altitude": uploader_altitude,
                            "uploaders": uploaders  # Include the uploaders list here
                        }
                    }
                }

                # Print or return the constructed response
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "error": "No telemetry data found for the specified serial and datetime."
                }
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        
        duration_mapping = {
            '0s': timedelta(seconds=0),
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
            start_time = server_time - duration_mapping[duration]

        # Filter telemetry data
        if serial:
            if start_time:
                telemetry_data = Telemetry.objects.filter(serial=serial, datetime__range=(start_time, server_time))
        else:
            if start_time:
                telemetry_data = Telemetry.objects.filter(datetime__range=(start_time, server_time))
        
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
        user_agent = request.headers.get('User-Agent', None)
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
            telemetry_data['user-agent'] = user_agent
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
