from flask import jsonify
from app import app, db
from models import Owners, Properties, PropertiesType, Tenants, Payments, MaintenanceRequests, Contracts, Rooms

@app.get('/api/dashboard')
def get_dashboard():
    # Total income
    income = db.session.query(db.func.sum(Payments.amount)).scalar() or 0

    # Counts
    tenant_count = Tenants.query.count()
    owner_count = Owners.query.count()

    # Maintenance stats
    maintenance_pending = MaintenanceRequests.query.filter_by(status='Pending').count()
    maintenance_completed = MaintenanceRequests.query.filter_by(status='Completed').count()

    # Properties
    properties = db.session.query(
        Properties.property_id,
        Properties.property_name,
        Properties.address,
        Owners.full_name.label('owner_name'),
        PropertiesType.type_name
    ).join(Owners, Properties.owner_id == Owners.owner_id) \
     .join(PropertiesType, Properties.type_id == PropertiesType.type_id, isouter=True).all()

    properties_list = [
        {
            'name': prop.property_name,
            'owner': prop.owner_name,
            'address': prop.address,
            'type': prop.type_name or "N/A"
        } for prop in properties
    ]

    # Contracts
    contracts = db.session.query(
        Contracts.contract_id,
        Tenants.full_name.label('tenant_name'),
        Properties.property_name.label('property_name'),
        Rooms.room_number.label('room_number'),
        Contracts.status
    ).join(Tenants, Contracts.tenant_id == Tenants.tenant_id) \
     .join(Rooms, Contracts.room_id == Rooms.room_id) \
     .join(Properties, Rooms.property_id == Properties.property_id).all()

    contracts_list = [
        {
            'id': c.contract_id,
            'tenant': c.tenant_name,
            'property': c.property_name,
            'room': c.room_number,
            'status': c.status
        } for c in contracts
    ]

    return jsonify({
        'income': float(income),
        'tenants': tenant_count,
        'owners': owner_count,
        'maintenance_pending': maintenance_pending,
        'maintenance_completed': maintenance_completed,
        'properties': properties_list,
        'contracts_table': contracts_list
    })
