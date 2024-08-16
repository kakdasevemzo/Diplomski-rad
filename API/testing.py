
import requests
 
# Making a PUT request
r = requests.put('https://sondehubapi-eceb35da85f7.herokuapp.com/api/sondes/telemetry/', data ={
    "software_name": "radiosonde_auto_rx",
    "software_version": "1.7.4",
    "uploader_callsign": "W5TUX",
    "time_received": "2024-08-16T11:18:23.237884Z",
    "manufacturer": "Vaisala",
    "type": "RS41",
    "serial": "W0434915",
    "frame": 2635,
    "datetime": "2024-08-16T11:17:50.468Z",
    "lat": 32.83891,
    "lon": -97.30071,
    "alt": 4002.28432,
    "subtype": "RS41-SG",
    "frequency": 404.801,
    "temp": 6.7,
    "humidity": 45.1,
    "vel_h": 6.15371,
    "vel_v": 10.56623,
    "pressure": 0,
    "heading": 193.09061,
    "batt": 3.0,
    "sats": 11,
    "xdata": "string",
    "snr": 8.1,
    "rssi": 0,
    "uploader_position": [
      0,
      0,
      200
    ],
    "uploader_antenna": "1/4 Monopole in attic"
  })
 
# check status code for response received
# success code - 200
print(r)
# print content of request
print(r.content)


