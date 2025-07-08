"""
Main Flask application for the Fitness Studio Booking API.
Provides endpoints for viewing classes, booking, viewing bookings, and admin timezone management.
"""
from flask import Flask, request, jsonify
from db import get_db_connection, init_db
from models import BookingRequest
from utils import convert_ist_to_timezone
from datetime import datetime
import pytz
import logging

def create_app(test_conn=None):
    app = Flask(__name__)
    conn = test_conn or get_db_connection()

    # Basic logging
    logging.basicConfig(level=logging.INFO)

    @app.route('/classes', methods=['GET'])
    def get_classes():
        tz = request.args.get('timezone', 'Asia/Kolkata')
        cur = conn.cursor()
        cur.execute('SELECT * FROM classes')
        classes = cur.fetchall()
        result = []
        for c in classes:
            # Convert datetime from IST to requested timezone
            try:
                dt_converted = convert_ist_to_timezone(c['datetime'], tz)
            except Exception:
                dt_converted = c['datetime']  # fallback
            result.append({
                'id': c['id'],
                'name': c['name'],
                'datetime': dt_converted,
                'instructor': c['instructor'],
                'available_slots': c['available_slots']
            })
        return jsonify(result), 200

    @app.route('/book', methods=['POST'])
    def book_class():
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
        # Check if class exists
        cur.execute('SELECT * FROM classes WHERE id = ?', (booking_req.class_id,))
        cls = cur.fetchone()
        if not cls:
            return jsonify({'error': 'Class not found'}), 404
        if cls['available_slots'] <= 0:
            return jsonify({'error': 'No slots available'}), 409
        # Book the class
        now_ist = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('''
            INSERT INTO bookings (class_id, client_name, client_email, booked_at)
            VALUES (?, ?, ?, ?)
        ''', (booking_req.class_id, booking_req.client_name, booking_req.client_email, now_ist))
        # Decrement available slots
        cur.execute('UPDATE classes SET available_slots = available_slots - 1 WHERE id = ?', (booking_req.class_id,))
        conn.commit()
        logging.info(f"Booking successful: {booking_req.client_name} for class {cls['name']}")
        return jsonify({'message': 'Booking successful'}), 201

    @app.route('/bookings', methods=['GET'])
    def get_bookings():
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Missing email parameter'}), 400
        cur = conn.cursor()
        cur.execute('''
            SELECT b.id, b.class_id, c.name as class_name, b.client_name, b.client_email, b.booked_at
            FROM bookings b
            JOIN classes c ON b.class_id = c.id
            WHERE b.client_email = ?
            ORDER BY b.booked_at DESC
        ''', (email,))
        bookings = cur.fetchall()
        result = []
        for b in bookings:
            result.append({
                'booking_id': b['id'],
                'class_id': b['class_id'],
                'class_name': b['class_name'],
                'client_name': b['client_name'],
                'client_email': b['client_email'],
                'booked_at': b['booked_at']
            })
        return jsonify(result), 200

    @app.route('/admin/change_timezone', methods=['POST'])
    def change_base_timezone():
        data = request.get_json()
        if not data or 'new_timezone' not in data:
            return jsonify({'error': 'Missing new_timezone in request body'}), 400
        new_tz = data['new_timezone']
        try:
            pytz.timezone(new_tz)
        except Exception:
            return jsonify({'error': 'Invalid timezone'}), 400
        cur = conn.cursor()
        cur.execute('SELECT id, datetime FROM classes')
        classes = cur.fetchall()
        ist = pytz.timezone('Asia/Kolkata')
        target = pytz.timezone(new_tz)
        for c in classes:
            # Convert from IST to new timezone, then store as new base
            dt_ist = ist.localize(datetime.strptime(c['datetime'], '%Y-%m-%d %H:%M:%S'))
            dt_new = dt_ist.astimezone(target)
            new_dt_str = dt_new.strftime('%Y-%m-%d %H:%M:%S')
            cur.execute('UPDATE classes SET datetime = ? WHERE id = ?', (new_dt_str, c['id']))
        conn.commit()
        logging.info(f"All class times updated to new base timezone: {new_tz}")
        return jsonify({'message': f'All class times updated to new base timezone: {new_tz}'}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app

if __name__ == '__main__':
    # Only for running the app normally
    conn = get_db_connection()
    init_db(conn)
    app = create_app(test_conn=conn)
    app.run(debug=True) 