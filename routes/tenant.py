import os
import uuid
import re
from flask import Flask, request, jsonify
from sqlalchemy import text
from werkzeug.utils import secure_filename
from app import app, db
from models import *


UPLOAD_FOLDER = 'static/images/tenants'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# -------------------------
# GET ALL TENANTS
# -------------------------
@app.get('/api/tenants')
def get_tenants():
    sql = text("""
        SELECT t.tenant_id, t.full_name, t.email, t.phone, t.id_card, t.address, t.image
        FROM tenants t
        LEFT JOIN contracts c ON t.tenant_id = c.tenant_id AND c.status='Unavailable'
    """)
    rows = db.session.execute(sql).mappings().all()
    tenants = [dict(r) for r in rows]
    return jsonify(tenants)

# GET TENANT BY ID
# -------------------------
@app.get('/api/tenants/<int:tenant_id>')
def get_tenant_by_id(tenant_id):
    sql = text("SELECT tenant_id, full_name, phone, email, id_card, address, image FROM tenants WHERE tenant_id = :tenant_id")
    result = db.session.execute(sql, {"tenant_id": tenant_id}).fetchone()
    if not result:
        return jsonify({'error': 'Tenant not found'}), 404
    return jsonify(dict(result._mapping))

# -------------------------
# CREATE TENANT
# -------------------------
@app.post('/api/tenants/create')
def create_tenant():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    id_card = request.form.get('id_card')
    address = request.form.get('address')
    image_file = request.files.get('image')

    if not full_name or not email:
        return jsonify({'error': 'Name and email are required'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email'}), 400

    image_path = None
    if image_file and allowed_file(image_file.filename):
        filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = f"/{UPLOAD_FOLDER}/{filename}"

    sql = text("""
        INSERT INTO tenants (full_name, email, phone, id_card, address, image)
        VALUES (:full_name, :email, :phone, :id_card, :address, :image)
    """)
    db.session.execute(sql, {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "id_card": id_card,
        "address": address,
        "image": image_path
    })
    db.session.commit()

    return jsonify({'message': 'Tenant created successfully'})

# -------------------------
# UPDATE TENANT
# -------------------------
@app.put('/api/tenants/update/<int:tenant_id>')
def update_tenant(tenant_id):
    name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    id_card = request.form.get('id_card')
    address = request.form.get('address')
    image_file = request.files.get('image')

    sql = text("SELECT * FROM tenants WHERE tenant_id = :tenant_id")
    tenant = db.session.execute(sql, {"tenant_id": tenant_id}).fetchone()
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404

    image_path = tenant.image
    if image_file and allowed_file(image_file.filename):
        filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = f"/{UPLOAD_FOLDER}/{filename}"

    sql_update = text("""
        UPDATE tenants
        SET full_name = :full_name,
            email = :email,
            phone = :phone,
            id_card = :id_card,
            address = :address,
            image = :image
        WHERE tenant_id = :tenant_id
    """)
    db.session.execute(sql_update, {
        "full_name": name,
        "email": email,
        "phone": phone,
        "id_card": id_card,
        "address": address,
        "image": image_path,
        "tenant_id": tenant_id
    })
    db.session.commit()

    return jsonify({'message': 'Tenant updated successfully'})

# -------------------------
# DELETE TENANT
# -------------------------
@app.delete('/api/tenants/delete')
def delete_tenant():
    data = request.get_json()
    tenant_id = data.get('id')
    if not tenant_id:
        return jsonify({'error': 'Tenant ID required'}), 400

    sql = text("SELECT * FROM tenants WHERE tenant_id = :tenant_id")
    tenant = db.session.execute(sql, {"tenant_id": tenant_id}).fetchone()
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404

    sql_delete = text("DELETE FROM tenants WHERE tenant_id = :tenant_id")
    db.session.execute(sql_delete, {"tenant_id": tenant_id})
    db.session.commit()

    return jsonify({'message': 'Tenant deleted successfully'})
