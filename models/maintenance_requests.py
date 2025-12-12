from app import db

class MaintenanceRequests(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id"))
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.tenant_id"))
    request_date = db.Column(db.Date)
    description = db.Column(db.String(255))
    status = db.Column(db.String(20))
    cost = db.Column(db.Numeric(10,2))
