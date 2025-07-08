"""
Unit tests for the Booking API.
Covers endpoints for classes, booking, bookings by email, overbooking, missing fields, and admin timezone change.
"""
import pytest
from app import create_app
from db import get_db_connection, init_db

# ----------------------
# Fixtures
# ----------------------

@pytest.fixture
def client():
    """
    Sets up a test client with a database connection.
    Initializes the database with test data.
    """
    conn = get_db_connection()
    init_db(conn)
    app = create_app(test_conn=conn)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ----------------------
# Classes Endpoints
# ----------------------

def test_get_classes(client):
    """
    GET /classes: Should return a list of classes with required fields.
    """
    resp = client.get('/classes')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert 'name' in data[0]
    assert 'available_slots' in data[0]

@pytest.mark.parametrize(
    "timezone,expected_status",
    [
        ("Asia/Kolkata", 200),
        ("UTC", 200),
        ("Europe/London", 200),
        ("Invalid/Timezone", 200),  # Should fallback, not error
    ]
)
def test_get_classes_various_timezones(client, timezone, expected_status):
    """
    GET /classes with various valid and invalid timezones.
    """
    resp = client.get(f'/classes?timezone={timezone}')
    assert resp.status_code == expected_status
    data = resp.get_json()
    assert isinstance(data, list)
    assert 'datetime' in data[0]

# ----------------------
# Booking Endpoints
# ----------------------

def test_book_class_success(client):
    """
    POST /book: Successful booking returns 201 and success message.
    """
    resp = client.post('/book', json={
        'class_id': 1,
        'client_name': 'Test',
        'client_email': 'test@test.com'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'Booking successful' in data['message']

def test_book_class_overbooking(client):
    """
    POST /book: Overbooking returns 409 Conflict.
    """
    for i in range(8):
        resp = client.post('/book', json={
            'class_id': 3,
            'client_name': f'User{i}',
            'client_email': f'user{i}@test.com'
        })
        assert resp.status_code == 201
    resp = client.post('/book', json={
        'class_id': 3,
        'client_name': 'Overbook',
        'client_email': 'overbook@test.com'
    })
    assert resp.status_code == 409
    data = resp.get_json()
    assert 'No slots available' in data['error']

@pytest.mark.parametrize(
    "payload,expected_status,expected_error",
    [
        ({'client_name': 'Test', 'client_email': 'test@test.com'}, 400, 'class_id is required'),
        ({'class_id': 1, 'client_email': 'test@test.com'}, 400, 'client_name is required'),
        ({'class_id': 1, 'client_name': 'Test'}, 400, 'client_email is required'),
        ({'class_id': 999, 'client_name': 'Test', 'client_email': 'test@test.com'}, 404, 'Class not found'),
        ({'class_id': 1, 'client_name': '   ', 'client_email': 'test@test.com'}, 400, 'client_name is required'),
        ({'class_id': 1, 'client_name': 'Test', 'client_email': '   '}, 400, 'client_email is required'),
    ]
)
def test_book_class_validation(client, payload, expected_status, expected_error):
    """
    POST /book: Parameterized validation for missing/invalid fields and non-existent class.
    """
    resp = client.post('/book', json=payload)
    assert resp.status_code == expected_status
    data = resp.get_json()
    assert expected_error in str(data['error'])

def test_book_class_missing_fields(client):
    """
    POST /book: Missing required fields returns 400 Bad Request.
    """
    resp = client.post('/book', json={
        'class_id': 1,
        'client_email': 'missing@test.com'
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'client_name is required' in str(data['error'])

# ----------------------
# Bookings Endpoints
# ----------------------

def test_get_all_bookings(client):
    """
    GET /bookings: Returns all bookings and correct fields, works when empty.
    """
    resp = client.get('/bookings')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

    client.post('/book', json={
        'class_id': 1,
        'client_name': 'All Booker',
        'client_email': 'allbooker@test.com'
    })
    resp = client.get('/bookings')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    booking = data[0]
    assert 'booking_id' in booking
    assert 'class_id' in booking
    assert 'class_name' in booking
    assert 'client_name' in booking
    assert 'client_email' in booking
    assert 'booked_at' in booking

def test_get_bookings_by_email(client):
    """
    GET /bookings?email=...: Returns only bookings for the specified email.
    """
    client.post('/book', json={
        'class_id': 1,
        'client_name': 'User1',
        'client_email': 'user1@test.com'
    })
    client.post('/book', json={
        'class_id': 2,
        'client_name': 'User2',
        'client_email': 'user2@test.com'
    })
    resp = client.get('/bookings?email=user1@test.com')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert all(b['client_email'] == 'user1@test.com' for b in data)

def test_get_bookings(client):
    """
    GET /bookings?email=...: Returns bookings for a specific email after booking.
    """
    client.post('/book', json={
        'class_id': 2,
        'client_name': 'Booker',
        'client_email': 'booker@test.com'
    })
    resp = client.get('/bookings?email=booker@test.com')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]['client_email'] == 'booker@test.com'

def test_get_bookings_empty(client):
    """
    GET /bookings: Returns empty list when there are no bookings.
    """
    resp = client.get('/bookings')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

# ----------------------
# Timezone Endpoints
# ----------------------

def test_admin_change_timezone(client):
    """
    POST /change_timezone: Successfully updates class datetimes and verifies timezone change.
    """
    resp = client.get('/classes')
    assert resp.status_code == 200
    data_ist = resp.get_json()
    dt_ist = data_ist[0]['datetime']

    resp = client.post('/change_timezone', json={"new_timezone": "UTC"})
    assert resp.status_code == 200
    assert 'All class times updated to new base timezone' in resp.get_json()['message']

    resp = client.get('/classes?timezone=UTC')
    assert resp.status_code == 200
    data_utc = resp.get_json()
    dt_utc = data_utc[0]['datetime']

    resp = client.get('/classes?timezone=Asia/Kolkata')
    assert resp.status_code == 200
    data_ist_after = resp.get_json()
    dt_ist_after = data_ist_after[0]['datetime']
    assert dt_utc != dt_ist_after

def test_admin_change_timezone_invalid(client):
    """
    POST /change_timezone: Invalid timezone string returns 400 error.
    """
    resp = client.post('/change_timezone', json={"new_timezone": "Invalid/Timezone"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'Invalid timezone' in data['error'] 