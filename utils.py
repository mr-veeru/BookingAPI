"""
Utility functions for the Fitness Studio Booking API.
Includes timezone conversion helpers.
"""
from datetime import datetime
import pytz

def convert_ist_to_timezone(dt_str, target_tz):
    ist = pytz.timezone('Asia/Kolkata')
    dt = ist.localize(datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S'))
    target = pytz.timezone(target_tz)
    return dt.astimezone(target).strftime('%Y-%m-%d %H:%M:%S') 