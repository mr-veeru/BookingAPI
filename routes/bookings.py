"""
Routes for booking creation and viewing bookings.
"""
from flask import Blueprint, request, jsonify, current_app
from models import BookingRequest, Booking
from typing import Any
from datetime import datetime
import pytz

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/book', methods=['POST'])
def book_class() -> Any:
    """
    Book a class for a client. Validates input and handles slot availability.
    """
    conn = current_app.config['DB_CONN']
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    booking_req = BookingRequest(
        class_id=data.get('class_id'),
        client_name=data.get('client_name'),
        client_email=data.get('client_email')
    )
    errors = booking_req.validate()
    if errors:
        return jsonify({'error': errors}), 400
    cur = conn.cursor()
    cur.execute('SELECT * FROM classes WHERE id = ?', (booking_req.class_id,))
    cls = cur.fetchone()
    if not cls:
        return jsonify({'error': 'Class not found'}), 404
    if cls['available_slots'] <= 0:
        return jsonify({'error': 'No slots available'}), 409
    now_ist = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute('''
        INSERT INTO bookings (class_id, client_name, client_email, booked_at)
        VALUES (?, ?, ?, ?)
    ''', (booking_req.class_id, booking_req.client_name, booking_req.client_email, now_ist))
    cur.execute('UPDATE classes SET available_slots = available_slots - 1 WHERE id = ?', (booking_req.class_id,))
    conn.commit()
    return jsonify({'message': 'Booking successful'}), 201

@bookings_bp.route('/bookings', methods=['GET']) 
def get_bookings() -> Any:
    """
    List all bookings.
    """
    conn = current_app.config['DB_CONN']
    cur = conn.cursor()
    cur.execute('''
        SELECT b.id, b.class_id, c.name as class_name, b.client_name, b.client_email, b.booked_at
        FROM bookings b
        JOIN classes c ON b.class_id = c.id
        ORDER BY b.booked_at DESC
    ''')
    bookings = cur.fetchall()
    result = []
    for b in bookings:
        try:
            ist = pytz.timezone('Asia/Kolkata')
            dt = ist.localize(datetime.strptime(b['booked_at'], '%Y-%m-%d %H:%M:%S'))
            booked_at_12hr = dt.strftime('%Y-%m-%d %I:%M %p')
        except Exception:
            booked_at_12hr = b['booked_at']
        booking_obj = Booking(
            id=b['id'],
            class_id=b['class_id'],
            client_name=b['client_name'],
            client_email=b['client_email'],
            booked_at=booked_at_12hr
        )
        booking_dict = booking_obj.__dict__
        booking_dict['class_name'] = b['class_name']
        booking_dict['booking_id'] = booking_dict.pop('id')
        result.append(booking_dict)
    return jsonify(result), 200 