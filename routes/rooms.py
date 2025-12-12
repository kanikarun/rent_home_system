from flask import jsonify
from app import app, db
from sqlalchemy import text
from models import *

@app.get('/api/rooms')
def get_rooms():
    try:
        query = text("""
            SELECT r.room_id, r.property_id, r.room_number, r.rent_price, r.description, r.status
            FROM rooms r
            INNER JOIN properties p ON r.property_id = p.property_id
            ORDER BY r.property_id, r.room_number
        """)
        rooms = db.session.execute(query).fetchall()
        result = []
        for r in rooms:
            result.append({
                "room_id": r.room_id,
                "property_id": r.property_id,
                "room_number": r.room_number,
                "rent_price": float(r.rent_price or 0.0),
                "description": r.description,
                "status": r.status
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
@app.delete('/api/rooms/<int:room_id>')
def delete_room(room_id):
    room = rooms.query.get(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404

    # Check if room has contracts
    contracts_count = contracts.query.filter_by(room_id=room_id).count()
    if contracts_count > 0:
        return jsonify({"error": "Cannot delete room: linked contracts exist"}), 400

    db.session.delete(room)
    db.session.commit()
    return jsonify({"message": "Room deleted"}), 200
