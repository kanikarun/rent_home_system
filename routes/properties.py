
from flask import request, jsonify
from sqlalchemy import text
from app import app, db
from models import *


# ===================== OWNERS =====================

@app.get('/api/owners')
def get_owners_api():
    owners = Owners.query.order_by(Owners.full_name).all()
    return jsonify([{
        "owner_id": o.owner_id,
        "full_name": o.full_name,
        "phone": o.phone,
        "email": o.email,
        "address": o.address
    } for o in owners]), 200


@app.post('/api/owners/create')
def create_owner():
    data = request.get_json()
    full_name = data.get("full_name")
    if not full_name:
        return jsonify({"error": "Owner name required"}), 400

    new_owner = Owners(
        full_name=full_name,
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address")
    )
    db.session.add(new_owner)
    db.session.commit()
    return jsonify({"message": "Owner created successfully", "owner_id": new_owner.owner_id,
                    "full_name": new_owner.full_name}), 201


# ===================== PROPERTY TYPES =====================
@app.get('/api/properties/types')
def get_property_types_api():
    types = PropertiesType.query.order_by(PropertiesType.type_name).all()
    return jsonify([{"type_id": t.type_id, "type_name": t.type_name} for t in types]), 200


@app.post('/api/properties/type/create')
def create_property_type_api():
    data = request.get_json()
    new_type = data.get("type")
    if not new_type:
        return jsonify({"error": "Type name is required"}), 400

    exists = PropertiesType.query.filter_by(type_name=new_type).first()
    if exists:
        return jsonify({"message": "Type already exists", "type": exists.type_name, "type_id": exists.type_id}), 200

    new_type_obj = PropertiesType(type_name=new_type)
    db.session.add(new_type_obj)
    db.session.commit()
    return jsonify(
        {"message": "Type created successfully", "type": new_type_obj.type_name, "type_id": new_type_obj.type_id}), 201


# ===================== PROPERTIES =====================
@app.get('/api/properties')
def get_properties_api():
    properties = db.session.query(Properties, Owners, PropertiesType) \
        .outerjoin(Owners, Properties.owner_id == Owners.owner_id) \
        .outerjoin(PropertiesType, Properties.type_id == PropertiesType.type_id) \
        .order_by(Properties.property_id.asc()).all()

    result = []
    for p, o, t in properties:
        result.append({
            "property_id": p.property_id,
            "property_name": p.property_name,
            "address": p.address,
            "status": p.status,
            "owner_id": o.owner_id if o else None,
            "owner_name": o.full_name if o else "-",
            "type_id": t.type_id if t else None,
            "type_name": t.type_name if t else "-"
        })
    return jsonify(result), 200


@app.get('/api/properties/<int:property_id>')
def get_property_by_id_api(property_id):
    p = Properties.query.get(property_id)
    if not p:
        return jsonify({"error": "Property not found"}), 404
    owner = Owners.query.get(p.owner_id)
    type_obj = PropertiesType.query.get(p.type_id)
    return jsonify({
        "property_id": p.property_id,
        "property_name": p.property_name,
        "address": p.address,
        "status": p.status,
        "owner_id": p.owner_id,
        "owner_name": owner.full_name if owner else "-",
        "type_id": p.type_id,
        "type_name": type_obj.type_name if type_obj else "-"
    }), 200


@app.get('/api/properties/<int:property_id>/rooms')
def get_property_rooms(property_id):
    p = Properties.query.get(property_id)
    if not p:
        return jsonify({"error": "Property not found"}), 404
    rooms = Rooms.query.filter_by(property_id=property_id).order_by(Rooms.room_id).all()
    return jsonify([{
        "room_number": r.room_number,
        "rent_price": r.rent_price,
        "description": r.description,
        "status": r.status
    } for r in rooms]), 200


@app.post('/api/properties/create')
def create_property():
    data = request.get_json()
    property_name = data.get("property_name")
    owner_id = data.get("owner_id")
    address = data.get("address")
    type_id = data.get("type_id")
    status_value = data.get("status", "Active")
    rooms = data.get("rooms", [])

    if not property_name or not owner_id or not address:
        return jsonify({"error": "Property Name, Owner, Address required"}), 400

    new_property = Properties(
        property_name=property_name,
        owner_id=owner_id,
        address=address,
        type_id=type_id,
        status=status_value
    )
    db.session.add(new_property)
    db.session.flush()  # get property_id

    for r in rooms:
        new_room = Rooms(
            property_id=new_property.property_id,
            room_number=r.get("room_number"),
            rent_price=r.get("rent_price", 0),
            description=r.get("description", ""),
            status=r.get("status", "Available")
        )
        db.session.add(new_room)
    db.session.commit()
    return jsonify({"message": "Property added", "property_id": new_property.property_id}), 201


@app.put('/api/properties/update/<int:property_id>')
def update_property_api(property_id):
    data = request.get_json()
    p = Properties.query.get(property_id)
    if not p:
        return jsonify({"error": "Property not found"}), 404

    p.property_name = data.get("property_name", p.property_name)
    p.owner_id = data.get("owner_id", p.owner_id)
    p.address = data.get("address", p.address)
    p.type_id = data.get("type_id", p.type_id)
    p.status = data.get("status", p.status)
    db.session.commit()

    if "rooms" in data:
        Rooms.query.filter_by(property_id=property_id).delete()
        for r in data["rooms"]:
            new_room = Rooms(
                property_id=property_id,
                room_number=r.get("room_number"),
                rent_price=r.get("rent_price", 0),
                description=r.get("description", ""),
                status=r.get("status", "Available")
            )
            db.session.add(new_room)
        db.session.commit()
    return jsonify({"message": "Property updated"}), 200


@app.delete('/api/properties/delete')
def delete_property_api():
    data = request.get_json()
    property_id = data.get("id")
    if not property_id:
        return jsonify({"error": "Property ID required"}), 400

    p = Properties.query.get(property_id)
    if not p:
        return jsonify({"error": "Property not found"}), 404

    # Cascade will automatically delete all associated rooms
    db.session.delete(p)
    db.session.commit()

    return jsonify({"message": "Property and its rooms deleted"}), 200
