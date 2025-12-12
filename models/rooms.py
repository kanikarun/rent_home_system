from app import db


class Rooms(db.Model):
    __tablename__ = "rooms"
    room_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.property_id"))
    room_number = db.Column(db.String(50))
    rent_price = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(255))
    status = db.Column(db.String(20), default="Available")
