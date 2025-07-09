"""
Routes for class listings and related endpoints.
"""
from flask import Blueprint, jsonify, current_app
from typing import Any

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/classes', methods=['GET'])
def get_classes() -> Any:
    """
    List all upcoming classes.
    """
    conn = current_app.config['DB_CONN']
    cur = conn.cursor()
    cur.execute('SELECT * FROM classes')
    classes = cur.fetchall()
    result = []
    for c in classes:
        result.append({
            'id': c['id'],
            'name': c['name'],
            'datetime': c['datetime'],
            'instructor': c['instructor'],
            'available_slots': c['available_slots']
        })
    return jsonify(result), 200 