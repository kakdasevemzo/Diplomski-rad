from django.urls import path
from .views import upload_telemetry


urlpatterns = [
    path('sondes/telemetry/', upload_telemetry, name='upload_telemetry'),
]