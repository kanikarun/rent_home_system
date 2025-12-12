from app import db


class Payments(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey("contracts.contract_id"))
    payment_date = db.Column(db.Date)
    amount = db.Column(db.Numeric(10,2))
    payment_method = db.Column(db.String(50))
    month_paid_for = db.Column(db.String(20))
    remarks = db.Column(db.String(255))
    total_paid = db.Column(db.Numeric(10, 2), default=0)
    remaining = db.Column(db.Numeric(10, 2), default=0)