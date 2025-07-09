"""
Data models for the Booking API.
Defines class, booking, and booking request schemas and validation.
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Class:
    """Represents a fitness class."""
    id: int
    name: str
    datetime: str  # ISO format string
    instructor: str
    available_slots: int

@dataclass
class Booking:
    """Represents a booking for a class."""
    id: int
    class_id: int
    client_name: str
    client_email: str
    booked_at: str  # ISO format string

@dataclass
class BookingRequest:
    """Request schema for booking a class, with validation."""
    class_id: int
    client_name: str
    client_email: str

    def validate(self) -> List[str]:
        """Validate the booking request fields. Returns a list of error messages."""
        errors: List[str] = []
        if not self.class_id:
            errors.append('class_id is required')
        if not self.client_name or not self.client_name.strip():
            errors.append('client_name is required')
        if not self.client_email or not self.client_email.strip():
            errors.append('client_email is required')
        return errors 