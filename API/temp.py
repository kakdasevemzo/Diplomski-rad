from datetime import timedelta,datetime
# Step 1: Round the milliseconds
original_datetime = datetime(year=2024, month=8, day=21, hour=15, minute=31, second=1, microsecond=5000)  # Assuming datetime_obj is your input datetime
print(original_datetime)
milliseconds = original_datetime.microsecond // 1000  # Get milliseconds part
rounded_milliseconds = round(milliseconds / 1000) * 1000  # Round to nearest value
print(f'Rounded_milliseconds {rounded_milliseconds}')
# Adjust the datetime with the rounded milliseconds
rounded_datetime = original_datetime.replace(microsecond=rounded_milliseconds * 1000)
print(rounded_datetime)
# Step 2: Define the time range (2 seconds before and after)
start_datetime = rounded_datetime - timedelta(seconds=2)
end_datetime = rounded_datetime + timedelta(seconds=2)
print(start_datetime, end_datetime)