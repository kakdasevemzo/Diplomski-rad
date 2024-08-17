from django.db import models
    
class Telemetry(models.Model):
    software_name = models.CharField(max_length=100)
    software_version = models.CharField(max_length=100)
    uploader_callsign = models.CharField(max_length=100)
    time_received = models.DateTimeField()
    manufacturer = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    serial = models.CharField(max_length=100)
    frame = models.IntegerField()
    datetime = models.DateTimeField()
    lat = models.FloatField()
    lon = models.FloatField()
    alt = models.FloatField()
    subtype = models.CharField(max_length=100)
    frequency = models.FloatField()
    temp = models.FloatField()
    humidity = models.FloatField()
    vel_h = models.FloatField()
    vel_v = models.FloatField()
    pressure = models.FloatField()
    heading = models.FloatField()
    batt = models.FloatField()
    sats = models.IntegerField()
    xdata = models.CharField(max_length=100)
    snr = models.FloatField()
    rssi = models.FloatField()
    uploader_position = models.JSONField()
    uploader_antenna = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.serial
