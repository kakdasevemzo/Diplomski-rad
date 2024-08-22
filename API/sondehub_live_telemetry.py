import threading
import time
import requests
from datetime import datetime
import sondehub
from email.utils import format_datetime
import sys
# A buffer to hold messages
message_buffer = []
packets_sent = 0
counter_lock = threading.Lock()
buffer_lock = threading.Lock()

def on_message(message):
    global message_buffer
    uploader_position = list(map(float, message.get("uploader_position", "0,0").split(',')))
    uploader_position.append(float(message.get("uploader_alt", "0")))
    transformed_data = {
        "software_name": message.get("software_name", ""),
        "software_version": message.get("software_version", ""),
        "uploader_callsign": message.get("uploader_callsign", ""),
        "time_received": message.get("time_received", ""),
        "manufacturer": message.get("manufacturer", ""),
        "type": message.get("type", ""),
        "serial": message.get("serial", ""),
        "frame": message.get("frame", 0),
        "datetime": message.get("datetime", ""),
        "lat": message.get("lat", 0.0),
        "lon": message.get("lon", 0.0),
        "alt": message.get("alt", 0.0),
        "subtype": message.get("subtype", "RS41-SG"),  # Defaulting to RS41-SG if not available
        "frequency": message.get("frequency", 0.0),
        "temp": message.get("temp", 0.0),
        "humidity": message.get("humidity", 0.0),
        "vel_h": message.get("vel_h", 0.0),
        "vel_v": message.get("vel_v", 0.0),
        "pressure": message.get("pressure", 0.0),
        "heading": message.get("heading", 0.0),
        "batt": message.get("batt", 0.0),
        "sats": message.get("sats", 0),
        "xdata": message.get("xdata", "string"),  # Assuming 'xdata' is not present in input
        "snr": message.get("snr", 0.0),
        "rssi": message.get("rssi", 0.0),
        "uploader_position": uploader_position,
        "uploader_antenna": message.get("uploader_antenna", ""),
        "burst_timer" : message.get("burst_timer", 65535),
        "tx_frequency" : message.get("tx_frequency", None),
        "user-agent" : message.get("user-agent", "Amazon CloudFront")
    }

    with buffer_lock:
        print(transformed_data.get('datetime'), transformed_data.get('serial'))
        message_buffer.append(transformed_data)

def send_batch():
    global message_buffer, packets_sent
    while True:
        with buffer_lock:
            if message_buffer:
                batch = message_buffer.copy()
                message_buffer = []

                last_message_time_received = batch[-1].get("time_received")
                
                if last_message_time_received:
                    # Convert time_received to a datetime object
                    last_message_datetime = datetime.strptime(last_message_time_received, "%Y-%m-%dT%H:%M:%S.%fZ")
                    
                    # Format the datetime as per RFC 7231 format
                    date_header_value = last_message_datetime.strftime(f"%a, %d %b %Y %H:%M:%S GMT")
                    print(date_header_value)
                    headers = {
                        'Date': date_header_value
                    }
                    try:
                        r = requests.put(url='https://sondehubapi-eceb35da85f7.herokuapp.com/api/sondes/telemetry/', json=batch, headers=headers)
                        with counter_lock:
                            packets_sent += len(batch)  # Update packet count
                        print(f"Sent {len(batch)} packets. Total packets sent: {packets_sent}")
                        print(r.status_code, r.reason)
                        print(r.text)
                    except requests.RequestException as e:
                        print(f"Request failed: {e}")
        time.sleep(1)  # Adjust the interval as needed

if __name__ == "__main__":
    # Start the batch sending thread
    threading.Thread(target=send_batch, daemon=True).start()

    # Initialize streaming
    sonde = None
    if len(sys.argv) > 1:
        sonde = sys.argv[1]
    print(f'Started streaming data...')

    if sonde:
        print(f'Streaming data for sonde: {sonde}')
    else:
        print(f'Streaming all data for all sondes!')
    test = sondehub.Stream(on_message=on_message, sondes=[sonde] if sonde else ["#"])

    while True:
        time.sleep(1)  # Replace with your main loop logic

