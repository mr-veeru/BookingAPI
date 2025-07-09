"""
Utility functions for the Booking API.
Includes timezone conversion helpers.
"""
from datetime import datetime
import pytz
from typing import Any

def convert_ist_to_timezone(dt_str: str, target_tz: str) -> str:
    """
    Convert a datetime string from IST to the specified target timezone.
    Returns the converted datetime as a string in '%Y-%m-%d %H:%M:%S' format.
    """
    ist = pytz.timezone('Asia/Kolkata')
    dt = ist.localize(datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S'))
    target = pytz.timezone(target_tz)
    return dt.astimezone(target).strftime('%Y-%m-%d %H:%M:%S') 