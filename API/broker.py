import sondehub
import sys

def on_message(message):

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
        "uploader_position": list(map(float, message.get("uploader_position", "0,0").split(','))),
        "uploader_antenna": message.get("uploader_antenna", "")
    }
    transformed_data["uploader_position"].append(message.get("uploader_alt", 0))
    print(transformed_data)
    # Return the transformed data inside a list
    return [transformed_data]

if __name__ == "__main__":
    sonde = None
    if len(sys.argv) > 1:
        sonde = sys.argv[1]
    print(f'Started streaming data...')

    if sonde:
        print(f'Streaming data for sonde: {sonde}')
    print(f'Streaming all data for all sondes!')
    test = sondehub.Stream(on_message=on_message, sondes=sonde if sonde else ["#"])

    while 1:
        pass
