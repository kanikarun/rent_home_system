from app import db


class Contracts(db.Model):
    contract_id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.tenant_id"))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id"))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    deposit_amount = db.Column(db.Numeric(10,2))
    monthly_rent = db.Column(db.Numeric(10,2))
    status = db.Column(db.String(20))