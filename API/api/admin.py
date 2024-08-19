from django.contrib import admin

# Register your models here.
from .models import Telemetry

class TelemetryAdmin(admin.ModelAdmin):
    list_filter = [
         "datetime",
         "frame"
    ]
    search_fields = (
        "serial",
    )

admin.site.register(Telemetry, TelemetryAdmin)