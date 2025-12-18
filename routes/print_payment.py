from flask import Flask, render_template, request
import json
from datetime import datetime, timedelta
import random
from collections import defaultdict
from app import app

@app.get('/print-payments')
def print_payments_get():
    return "<p>Please select payments from the main page to print.</p>"

@app.post('/print-payments')
def print_payments_post():
    payments_json = request.form.get('payments', '[]')
    try:
        payments = json.loads(payments_json)
    except:
        payments = []

    # Clean numeric columns
    for p in payments:
        # amount = monthly rent
        try:
            p[5] = float(str(p[5]).replace('$','').replace(',','').strip())
        except:
            p[5] = 0.0

        # total_paid
        try:
            p[6] = float(str(p[6]).replace('$','').replace(',','').strip())
        except:
            p[6] = 0.0

    # Accumulate total_paid per tenant and month
    totals = defaultdict(float)  # key = (tenant, month)
    for p in payments:
        key = (p[1], p[3])  # tenant name, month
        totals[key] += p[6]

    # Calculate remaining per row based on accumulated payments
    for p in payments:
        key = (p[1], p[3])
        p[7] = max(p[5] - totals[key], 0.0)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # BILL TO LOGIC
    tenants = list({p[1] for p in payments})
    rooms = sorted({str(p[2]) for p in payments})
    bill_to_name = tenants[0] if len(tenants) == 1 else "ADMIN"
    bill_to_type = "Tenant" if len(tenants) == 1 else "System Account"
    bill_to_rooms = ", ".join(rooms)
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000,9999)}"
    due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    return render_template(
        'print-payment.html',
        payments=payments,
        now=now,
        bill_to_name=bill_to_name,
        bill_to_type=bill_to_type,
        bill_to_rooms=bill_to_rooms,
        invoice_number=invoice_number,
        due_date=due_date
    )
