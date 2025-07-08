"""
Data models for the Fitness Studio Booking API.
Defines class, booking, and booking request schemas and validation.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Class:
    id: int
    name: str
    datetime: str  # ISO format string
    instructor: str
    available_slots: int

@dataclass
class Booking:
    id: int
    class_id: int
    client_name: str
    client_email: str
    booked_at: str  # ISO format string

@dataclass
class BookingRequest:
    class_id: int
    client_name: str
    client_email: str

    def validate(self):
        errors = []
        if not self.class_id:
            errors.append('class_id is required')
        if not self.client_name or not self.client_name.strip():
            errors.append('client_name is required')
        if not self.client_email or not self.client_email.strip():
            errors.append('client_email is required')
        return errors 