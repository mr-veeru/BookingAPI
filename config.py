"""
Configuration classes for the Booking API.
Defines base, development, testing, and production settings.
"""

class Config:
    """Base configuration."""
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"
    DEBUG: bool = False
    TESTING: bool = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG: bool = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING: bool = True
    DEBUG: bool = True
