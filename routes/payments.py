from flask import request, jsonify
from sqlalchemy import text
from datetime import datetime, date
from app import app, db


# Helper date-format function
def fmt_date(d):
    if isinstance(d, (datetime, date)):
        return d.strftime("%Y-%m-%d")
    return d or ""

# ============================================================
#                 GET PAYMENT
# ============================================================
@app.get('/api/payments')
def get_all_payments():
    try:
        query = text("""
            SELECT 
                p.payment_id,
                p.contract_id,
                p.payment_date,
                p.amount,
                p.payment_method,
                p.month_paid_for,
                p.remarks,
                c.tenant_id,
                c.room_id,
                c.monthly_rent,
                c.status,          -- add status
                t.full_name AS tenant,
                r.room_number
            FROM payments p
            LEFT JOIN contracts c ON p.contract_id = c.contract_id
            LEFT JOIN tenants t ON c.tenant_id = t.tenant_id
            LEFT JOIN rooms r ON c.room_id = r.room_id
            ORDER BY p.payment_id ASC
        """)

        rows = db.session.execute(query).fetchall()
        result = []

        for p in rows:
            row = p._mapping

            contract_id = row['contract_id']
            month_paid_for = row['month_paid_for'] or ""
            monthly_rent = float(row['monthly_rent'] or 0)
            payment_date = row['payment_date']

            # Handle payment_date safely
            if isinstance(payment_date, (datetime, date)):
                payment_date_str = payment_date.strftime("%Y-%m-%d")
            else:
                payment_date_str = payment_date or ""

            # Calculate total paid
            paid_res = db.session.execute(
                text("""
                    SELECT COALESCE(SUM(amount),0) AS total_paid
                    FROM payments
                    WHERE contract_id=:cid AND month_paid_for=:month
                """),
                {"cid": contract_id, "month": month_paid_for}
            ).fetchone()
            total_paid = float(paid_res[0] or 0)
            remaining = monthly_rent - total_paid

            result.append({
                "payment_id": row['payment_id'],
                "contract_id": contract_id,
                "tenant": row['tenant'] or "",
                "tenant_id": row['tenant_id'],
                "room_id": row['room_id'],
                "room_number": row['room_number'] or "",
                "monthly_rent": monthly_rent,
                "payment_date": payment_date_str,
                "amount": float(row['amount'] or 0),
                "payment_method": row['payment_method'] or "",
                "month_paid_for": month_paid_for,
                "remarks": row['remarks'] or "",
                "total_paid": total_paid,
                "remaining": remaining,
                "status": row['status'] or ""   # <-- include status
            })

        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ============================================================
#                 CREATE PAYMENT
# ============================================================
@app.post('/api/payments/create')
def create_payment():
    data = request.get_json()
    try:
        payment_date = datetime.strptime(data['payment_date'], "%Y-%m-%d").date()
        contract_id = data['contract_id']
        month = data['month_paid_for']
        amount = float(data.get('amount', 0))

        # Get contract's monthly rent
        contract_res = db.session.execute(
            text("SELECT monthly_rent, status FROM contracts WHERE contract_id=:cid"),
            {"cid": contract_id}
        ).fetchone()
        if not contract_res:
            return jsonify({"error": "Contract not found"}), 400

        if contract_res.status != "Available":
            return jsonify({"error": "Cannot add payment to unavailable contract"}), 400
        monthly_rent = float(contract_res.monthly_rent or 0)

        # Calculate total paid for this month (including this new payment)
        paid_res = db.session.execute(
            text("SELECT COALESCE(SUM(amount),0) AS total_paid FROM payments WHERE contract_id=:cid AND month_paid_for=:month"),
            {"cid": contract_id, "month": month}
        ).fetchone()
        total_paid = float(paid_res.total_paid or 0) + amount
        remaining = monthly_rent - total_paid

        # Insert payment
        db.session.execute(
            text("""
                INSERT INTO payments
                (contract_id, payment_date, amount, payment_method, month_paid_for, remarks, total_paid, remaining)
                VALUES (:contract_id, :payment_date, :amount, :payment_method, :month_paid_for, :remarks, :total_paid, :remaining)
            """),
            {
                "contract_id": contract_id,
                "payment_date": payment_date,
                "amount": amount,
                "payment_method": data.get('payment_method', ''),
                "month_paid_for": month,
                "remarks": data.get('remarks', ''),
                "total_paid": total_paid,
                "remaining": remaining
            }
        )
        db.session.commit()
        return jsonify({"message": "Payment added"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============================================================
#                 UPDATE PAYMENT
# ============================================================
@app.put('/api/payments/<int:pid>')
def update_payment(pid):
    data = request.get_json()
    try:
        payment_date = datetime.strptime(data['payment_date'], "%Y-%m-%d").date()
        contract_id = data['contract_id']
        month = data['month_paid_for']
        amount = float(data.get('amount', 0))

        # Get contract's monthly rent
        contract_res = db.session.execute(
            text("SELECT monthly_rent, status FROM contracts WHERE contract_id=:cid"),
            {"cid": contract_id}
        ).fetchone()
        if not contract_res:
            return jsonify({"error": "Contract not found"}), 400

        if contract_res.status != "Available":
            return jsonify({"error": "Cannot add payment to unavailable contract"}), 400
        monthly_rent = float(contract_res.monthly_rent or 0)

        # Calculate total paid for this month excluding current payment
        paid_res = db.session.execute(
            text("SELECT COALESCE(SUM(amount),0) AS total_paid FROM payments WHERE contract_id=:cid AND month_paid_for=:month AND payment_id<>:pid"),
            {"cid": contract_id, "month": month, "pid": pid}
        ).fetchone()
        total_paid = float(paid_res.total_paid or 0) + amount
        remaining = monthly_rent - total_paid

        # Update payment
        db.session.execute(
            text("""
                UPDATE payments
                SET contract_id=:contract_id,
                    payment_date=:payment_date,
                    amount=:amount,
                    payment_method=:payment_method,
                    month_paid_for=:month_paid_for,
                    remarks=:remarks,
                    total_paid=:total_paid,
                    remaining=:remaining
                WHERE payment_id=:pid
            """),
            {
                "contract_id": contract_id,
                "payment_date": payment_date,
                "amount": amount,
                "payment_method": data.get('payment_method', ''),
                "month_paid_for": month,
                "remarks": data.get('remarks', ''),
                "total_paid": total_paid,
                "remaining": remaining,
                "pid": pid
            }
        )
        db.session.commit()
        return jsonify({"message": "Payment updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============================================================
#                 DELETE PAYMENT
# ============================================================
@app.delete('/api/payments/<int:pid>')
def delete_payment(pid):
    try:
        db.session.execute(
            text("DELETE FROM payments WHERE payment_id = :pid"),
            {"pid": pid}
        )
        db.session.commit()
        return jsonify({"message": "Payment deleted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
