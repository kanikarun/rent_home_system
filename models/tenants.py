from app import db

class Tenants(db.Model):
    tenant_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    image = db.Column(db.String(255))
    id_card = db.Column(db.String(50))
    address = db.Column(db.String(255))