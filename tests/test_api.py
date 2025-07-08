"""
Unit tests for the Fitness Studio Booking API.
Covers endpoints for classes, booking, bookings by email, overbooking, missing fields, and admin timezone change.
"""
import pytest
from app import create_app
from db import get_db_connection, init_db

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

def test_get_classes(client):
    """
    Tests the GET /classes endpoint.
    Verifies that the endpoint returns a list of classes and that the data includes 'name' and 'available_slots'.
    """
    resp = client.get('/classes')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert 'name' in data[0]
    assert 'available_slots' in data[0]

def test_book_class_success(client):
    """
    Tests the POST /book endpoint for successful booking.
    Verifies that the booking is successful and returns the expected message.
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
    Tests the POST /book endpoint for overbooking.
    Verifies that the endpoint returns a 409 Conflict response when trying to book more slots than available.
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

def test_book_class_missing_fields(client):
    """
    Tests the POST /book endpoint for missing required fields.
    Verifies that the endpoint returns a 400 Bad Request response when 'client_name' is missing.
    """
    resp = client.post('/book', json={
        'class_id': 1,
        'client_email': 'missing@test.com'
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'client_name is required' in str(data['error'])

def test_get_bookings(client):
    """
    Tests the GET /bookings endpoint for retrieving bookings by email.
    Verifies that the endpoint returns a list of bookings for a specific email.
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

def test_admin_change_timezone(client):
    """
    Tests the POST /admin/change_timezone endpoint for changing the base timezone.
    Verifies that the endpoint successfully updates class datetimes and that fetching classes in different timezones
    returns different results.
    """
    # Get original class datetimes in IST
    resp = client.get('/classes')
    assert resp.status_code == 200
    data_ist = resp.get_json()
    dt_ist = data_ist[0]['datetime']

    # Change base timezone to UTC
    resp = client.post('/admin/change_timezone', json={"new_timezone": "UTC"})
    assert resp.status_code == 200
    assert 'All class times updated to new base timezone' in resp.get_json()['message']

    # Get classes again, should now be stored in UTC
    resp = client.get('/classes?timezone=UTC')
    assert resp.status_code == 200
    data_utc = resp.get_json()
    dt_utc = data_utc[0]['datetime']

    # The datetime string should be the same as before, since now the base is UTC
    # But if we fetch in IST, it should be different
    resp = client.get('/classes?timezone=Asia/Kolkata')
    assert resp.status_code == 200
    data_ist_after = resp.get_json()
    dt_ist_after = data_ist_after[0]['datetime']
    assert dt_utc != dt_ist_after  # Should be different after base timezone change 

def test_get_classes_invalid_timezone(client):
    """
    Tests GET /classes with an invalid timezone parameter.
    Should fallback to original datetime or return a valid response.
    """
    resp = client.get('/classes?timezone=Invalid/Timezone')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    # Should still return class data, but datetimes may not be converted
    assert 'datetime' in data[0]


def test_admin_change_timezone_invalid(client):
    """
    Tests POST /admin/change_timezone with an invalid timezone string.
    Should return a 400 error with appropriate message.
    """
    resp = client.post('/admin/change_timezone', json={"new_timezone": "Invalid/Timezone"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'Invalid timezone' in data['error']


def test_get_bookings_empty(client):
    """
    Tests GET /bookings for an email with no bookings.
    Should return an empty list.
    """
    resp = client.get('/bookings?email=emptyuser@test.com')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 0 