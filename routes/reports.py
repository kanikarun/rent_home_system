from flask import Flask, jsonify
from sqlalchemy import text
from datetime import datetime
from app import app, db

# ===================== REPORTS API =====================

@app.get('/api/reports/summary')
def get_summary():
    try:
        today = datetime.today()
        month = today.month
        year = today.year

        # Total income this month
        sql_income = text("""
            SELECT COALESCE(SUM(amount),0) as total_income
            FROM payments
            WHERE CAST(strftime('%m', payment_date) AS INTEGER) = :month
              AND CAST(strftime('%Y', payment_date) AS INTEGER) = :year
        """)
        total_income = db.session.execute(sql_income, {"month": month, "year": year}).scalar()

        # Active contracts (status = 'Unavailable')
        sql_active = text("""
            SELECT COUNT(*)
            FROM contracts
            WHERE status='Available'
              AND start_date <= :today
              AND end_date >= :today
        """)
        active_contracts = db.session.execute(sql_active, {"today": today.date()}).scalar()

        # Outstanding payments (active contracts with missing/insufficient payments)
        sql_outstanding = text("""
            SELECT COUNT(*)
            FROM contracts c
            LEFT JOIN payments p ON c.contract_id = p.contract_id
            WHERE c.status='Unavailable'
              AND (p.contract_id IS NULL OR p.amount < c.monthly_rent)
        """)
        outstanding_tenants = db.session.execute(sql_outstanding).scalar()

        # Maintenance costs this month
        sql_maint = text("""
            SELECT COALESCE(SUM(cost),0)
            FROM maintenance_requests
            WHERE status='Completed'
              AND CAST(strftime('%m', request_date) AS INTEGER) = :month
              AND CAST(strftime('%Y', request_date) AS INTEGER) = :year
        """)
        maintenance_cost = db.session.execute(sql_maint, {"month": month, "year": year}).scalar()

        return jsonify({
            "total_income": float(total_income),
            "active_contracts": active_contracts,
            "outstanding_tenants": outstanding_tenants,
            "maintenance_cost": float(maintenance_cost)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get('/api/reports/monthly_income')
def monthly_income_report():
    try:
        sql = text("""
            SELECT 
                CAST(strftime('%m', p.payment_date) AS INTEGER) as month,
                COALESCE(SUM(p.amount),0) as total_collected,
                COALESCE(SUM(c.monthly_rent),0) as total_expected,
                COALESCE(SUM(c.monthly_rent),0) - COALESCE(SUM(p.amount),0) as difference
            FROM contracts c
            LEFT JOIN payments p ON c.contract_id = p.contract_id
            GROUP BY month
            ORDER BY month
        """)
        rows = db.session.execute(sql).mappings().all()
        report = [dict(r) for r in rows]
        return jsonify(report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get('/api/reports/outstanding_payments')
def outstanding_payments():
    try:
        sql = text("""
            SELECT t.full_name AS tenant, r.room_number, 
                   strftime('%m', c.start_date) AS month_due,
                   c.monthly_rent AS amount
            FROM contracts c
            LEFT JOIN tenants t ON c.tenant_id = t.tenant_id
            LEFT JOIN rooms r ON c.room_id = r.room_id
            LEFT JOIN payments p ON c.contract_id = p.contract_id
            WHERE c.status='Unavailable'
              AND (p.contract_id IS NULL OR p.amount < c.monthly_rent)
        """)
        rows = db.session.execute(sql).mappings().all()
        report = [dict(r) for r in rows]
        return jsonify(report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get('/api/reports/maintenance_summary')
def maintenance_summary():
    try:
        sql = text("""
            SELECT CAST(strftime('%m', request_date) AS INTEGER) as month,
                   COALESCE(SUM(cost),0) as total_maintenance_cost,
                   SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) as completed_requests
            FROM maintenance_requests
            GROUP BY month
            ORDER BY month
        """)
        rows = db.session.execute(sql).mappings().all()
        report = [dict(r) for r in rows]
        return jsonify(report)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
