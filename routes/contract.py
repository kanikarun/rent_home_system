from flask import Flask, request, jsonify
from sqlalchemy import text
from datetime import datetime, date
from app import app, db


today = date.today()
# ===================== GET ALL CONTRACTS =====================
@app.get('/api/contracts')
def get_all_contracts():
    query = text("""
        SELECT c.contract_id,
               c.tenant_id,
               c.room_id,
               c.start_date,
               c.end_date,
               c.deposit_amount,
               c.monthly_rent,
               c.status,
               t.full_name AS tenant,
               r.room_number,
               r.property_id,
               p.property_name AS property
        FROM contracts c
        LEFT JOIN tenants t ON c.tenant_id = t.tenant_id
        LEFT JOIN rooms r ON c.room_id = r.room_id
        LEFT JOIN properties p ON r.property_id = p.property_id
        ORDER BY c.contract_id ASC
    """)
    rows = db.session.execute(query).fetchall()

    def fmt_date(d):
        if isinstance(d, (datetime, date)):
            return d.strftime("%Y-%m-%d")
        return d or ""

    result = []
    for c in rows:
        result.append({
            "contract_id": c.contract_id,
            "tenant_id": c.tenant_id,
            "tenant": c.tenant,
            "property_id": c.property_id,
            "property": c.property,
            "room_id": c.room_id,
            "room_number": c.room_number,
            "start_date": fmt_date(c.start_date),
            "end_date": fmt_date(c.end_date),
            "deposit_amount": float(c.deposit_amount or 0),
            "monthly_rent": float(c.monthly_rent or 0),
            "status": c.status
        })
    return jsonify(result), 200
# ===================== ACTIVE CONTRACT =====================
@app.get('/api/contracts/active')
def get_active_contracts():
    sql = text("""
        SELECT c.contract_id, c.room_id, r.room_number,
               c.tenant_id, t.full_name AS tenant_name
        FROM contracts c
        LEFT JOIN tenants t ON c.tenant_id = t.tenant_id
        LEFT JOIN rooms r ON c.room_id = r.room_id
        WHERE c.status='Available'
    """)
    rows = db.session.execute(sql).mappings().all()
    contracts = [{
        "contract_id": r["contract_id"],
        "room_id": r["room_id"],
        "room_number": r["room_number"],
        "tenant_id": r["tenant_id"],
        "tenant_name": r["tenant_name"]
    } for r in rows]
    return jsonify(contracts)

# ===================== CREATE CONTRACT =====================
@app.post('/api/contracts')
def create_contract():
    data = request.get_json()
    try:
        start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(data['end_date'], "%Y-%m-%d").date()
        status = data.get('status', 'Available')  # use front-end value

        if end_date < start_date:
            return jsonify({"error": "End date must be after start date"}), 400

        # Check overlapping contracts
        overlap = db.session.execute(
            text("""
                SELECT 1 FROM contracts
                WHERE room_id = :room_id
                  AND NOT (end_date < :start_date OR start_date > :end_date)
            """),
            {"room_id": data['room_id'], "start_date": start_date, "end_date": end_date}
        ).fetchone()
        if overlap:
            return jsonify({"error": "Room is already booked for selected dates"}), 400

        # Insert contract
        db.session.execute(
            text("""
                INSERT INTO contracts
                (tenant_id, room_id, start_date, end_date, deposit_amount, monthly_rent, status)
                VALUES (:tenant_id, :room_id, :start_date, :end_date, :deposit_amount, :monthly_rent, :status)
            """),
            {
                "tenant_id": data['tenant_id'],
                "room_id": data['room_id'],
                "start_date": start_date,
                "end_date": end_date,
                "deposit_amount": data.get('deposit_amount', 0),
                "monthly_rent": data.get('monthly_rent', 0),
                "status": status
            }
        )
        db.session.commit()
        return jsonify({"message": "Contract created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===================== UPDATE CONTRACT =====================
@app.put('/api/contracts/<int:contract_id>')
def update_contract(contract_id):
    data = request.get_json()
    try:
        start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(data['end_date'], "%Y-%m-%d").date()
        status = data.get('status', 'Available')

        if end_date < start_date:
            return jsonify({"error": "End date must be after start date"}), 400

        # Check if user tries to set status to Available for a contract that hasn't ended
        if status == 'Available' and end_date <= today:
            return jsonify({"error": "Cannot set status to Available while contract end date has passed."}), 400
        # Check overlapping contracts excluding current
        overlap = db.session.execute(
            text("""
                SELECT 1 FROM contracts
                WHERE contract_id != :contract_id
                  AND room_id = :room_id
                  AND NOT (end_date < :start_date OR start_date > :end_date)
            """),
            {
                "contract_id": contract_id,
                "room_id": data['room_id'],
                "start_date": start_date,
                "end_date": end_date
            }
        ).fetchone()
        if overlap:
            return jsonify({"error": "Room is already booked for selected dates"}), 400

        # Update contract including status
        db.session.execute(
            text("""
                UPDATE contracts SET
                    tenant_id = :tenant_id,
                    room_id = :room_id,
                    start_date = :start_date,
                    end_date = :end_date,
                    deposit_amount = :deposit_amount,
                    monthly_rent = :monthly_rent,
                    status = :status
                WHERE contract_id = :contract_id
            """),
            {
                "tenant_id": data['tenant_id'],
                "room_id": data['room_id'],
                "start_date": start_date,
                "end_date": end_date,
                "deposit_amount": data.get('deposit_amount', 0),
                "monthly_rent": data.get('monthly_rent', 0),
                "status": status,
                "contract_id": contract_id
            }
        )
        db.session.commit()
        return jsonify({"message": "Contract updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===================== DELETE CONTRACT =====================
@app.delete('/api/contracts/<int:contract_id>')
def delete_contract(contract_id):
    try:
        db.session.execute(
            text("DELETE FROM contracts WHERE contract_id=:id"),
            {"id": contract_id}
        )
        db.session.commit()
        return jsonify({"message": "Contract deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400