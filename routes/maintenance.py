from flask import Flask, request, jsonify
from sqlalchemy import text
from datetime import datetime
from app import app, db
from models import *

# ===== GET ALL MAINTENANCE REQUESTS =====
@app.get('/api/maintenance')
def get_maintenance_requests():
    sql = text("""
        SELECT m.request_id, m.room_id, r.room_number, m.tenant_id, t.full_name AS tenant_name,
               m.request_date, m.description, m.status, m.cost
        FROM maintenance_requests m
        LEFT JOIN tenants t ON m.tenant_id = t.tenant_id
        LEFT JOIN rooms r ON m.room_id = r.room_id
        ORDER BY m.request_id
    """)
    try:
        rows = db.session.execute(sql).mappings().all()
        requests = [{
            "request_id": r["request_id"],
            "room_id": r["room_id"],
            "room_number": r["room_number"],
            "tenant_id": r["tenant_id"],
            "tenant_name": r["tenant_name"],
            "request_date": r["request_date"],  # already a string
            "description": r["description"],
            "status": r["status"],
            "cost": float(r["cost"]) if r["cost"] else 0
        } for r in rows]
        return jsonify(requests), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== GET SINGLE MAINTENANCE REQUEST =====
@app.get('/api/maintenance/<int:request_id>')
def get_maintenance_request_by_id(request_id):
    sql = text("""
        SELECT m.request_id, m.room_id, r.room_number, m.tenant_id, t.full_name AS tenant_name,
               m.request_date, m.description, m.status, m.cost
        FROM maintenance_requests m
        LEFT JOIN tenants t ON m.tenant_id = t.tenant_id
        LEFT JOIN rooms r ON m.room_id = r.room_id
        WHERE m.request_id = :request_id
    """)
    try:
        row = db.session.execute(sql, {"request_id": request_id}).mappings().first()
        if not row:
            return jsonify({"error": "Maintenance request not found"}), 404

        return jsonify({
            "request_id": row["request_id"],
            "room_id": row["room_id"],
            "room_number": row["room_number"],
            "tenant_id": row["tenant_id"],
            "tenant_name": row["tenant_name"],
            "request_date": row["request_date"],  # already a string
            "description": row["description"],
            "status": row["status"],
            "cost": float(row["cost"]) if row["cost"] else 0
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post('/api/maintenance/create')
def create_maintenance_request():
    data = request.get_json()
    room_id = data.get("room_id")
    tenant_id = data.get("tenant_id")
    request_date = data.get("request_date")
    description = data.get("description")
    status = data.get("status", "Pending")
    cost = data.get("cost", 0)

    if not room_id or not tenant_id or not request_date or not description:
        return jsonify({"error": "room_id, tenant_id, request_date, description are required"}), 400

    try:
        sql = text("""
            INSERT INTO maintenance_requests (room_id, tenant_id, request_date, description, status, cost)
            VALUES (:room_id, :tenant_id, :request_date, :description, :status, :cost)
        """)
        db.session.execute(sql, {
            "room_id": room_id,
            "tenant_id": tenant_id,
            "request_date": request_date,
            "description": description,
            "status": status,
            "cost": cost
        })
        db.session.commit()
        return jsonify({"message": "Maintenance request created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.put('/api/maintenance/update/<int:request_id>')
def update_maintenance_request(request_id):
    data = request.get_json()
    try:
        sql = text("""
            UPDATE maintenance_requests
            SET room_id = :room_id,
                tenant_id = :tenant_id,
                request_date = :request_date,
                description = :description,
                status = :status,
                cost = :cost
            WHERE request_id = :request_id
        """)
        db.session.execute(sql, {
            "room_id": data.get("room_id"),
            "tenant_id": data.get("tenant_id"),
            "request_date": data.get("request_date"),
            "description": data.get("description"),
            "status": data.get("status"),
            "cost": data.get("cost"),
            "request_id": request_id
        })
        db.session.commit()
        return jsonify({"message": "Maintenance request updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.delete('/api/maintenance/delete/<int:request_id>')
def delete_maintenance_request(request_id):
    try:
        sql = text("DELETE FROM maintenance_requests WHERE request_id = :request_id")
        db.session.execute(sql, {"request_id": request_id})
        db.session.commit()
        return jsonify({"message": "Maintenance request deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
