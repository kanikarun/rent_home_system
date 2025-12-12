from app import db

class Properties(db.Model):
    property_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.owner_id"))
    property_name = db.Column(db.String(100))
    address = db.Column(db.String(255))
    type_id = db.Column(
        db.Integer,
        db.ForeignKey("properties_type.type_id", name="fk_properties_type_id")
    )
    status = db.Column(db.String(20))

    # Add relationship to Rooms with cascade delete
    rooms = db.relationship(
        "Rooms",
        backref="property",
        cascade="all, delete-orphan"
    )