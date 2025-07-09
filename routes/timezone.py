"""
Routes for changing the base timezone.
"""
from datetime import datetime
from typing import Any
import pytz
from flask import Blueprint, current_app, jsonify, request

timezone_bp = Blueprint('timezone', __name__)

@timezone_bp.route('/change_timezone', methods=['POST'])
def change_base_timezone() -> Any:
    """
    Change the base timezone for all classes.
    """
    conn = current_app.config['DB_CONN']
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
    ist = pytz.timezone(current_app.config['DEFAULT_TIMEZONE'])
    target = pytz.timezone(new_tz)
    for c in classes:
        dt_ist = ist.localize(datetime.strptime(c['datetime'], '%Y-%m-%d %H:%M:%S'))
        dt_new = dt_ist.astimezone(target)
        new_dt_str = dt_new.strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('UPDATE classes SET datetime = ? WHERE id = ?', (new_dt_str, c['id']))
    conn.commit()
    return jsonify({'message': f'All class times updated to new base timezone: {new_tz}'}), 200
