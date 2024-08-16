from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TelemetrySerializer
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from .models import Telemetry
from datetime import timedelta


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
        # Access headers
        print(f'Request method PUT: {request}')
        print(f'Request method PUT data: {request.data}')
        date_header = request.headers.get('Date')
        user_agent = request.headers.get('User-Agent')
        print(f"date_header: {date_header}, user_agent: {user_agent}")
        # Parse the date header if needed
        # if date_header:
        #     try:
        #         date_parsed = parse_datetime(date_header)
        #         if date_parsed is None:
        #             date_parsed = datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %Z')
        #     except ValueError:
        #         return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Proceed with the standard serialization and saving process
        serializer = TelemetrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
