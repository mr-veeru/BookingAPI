"""
Routes for class listings and related endpoints.
"""
from flask import Blueprint, request, jsonify, current_app
from utils import convert_ist_to_timezone
from typing import Any

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/classes', methods=['GET'])
def get_classes() -> Any:
    """
    List all upcoming classes, with optional timezone conversion.
    """
    conn = current_app.config['DB_CONN']
    tz = request.args.get('timezone', current_app.config.get('DEFAULT_TIMEZONE', 'Asia/Kolkata'))
    cur = conn.cursor()
    cur.execute('SELECT * FROM classes')
    classes = cur.fetchall()
    result = []
    for c in classes:
        try:
            dt_converted = convert_ist_to_timezone(c['datetime'], tz)
        except Exception:
            dt_converted = c['datetime']
        result.append({
            'id': c['id'],
            'name': c['name'],
            'datetime': dt_converted,
            'instructor': c['instructor'],
            'available_slots': c['available_slots']
        })
    return jsonify(result), 200 