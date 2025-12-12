import re
from datetime import datetime

from app import app, db
from flask import jsonify, request
from sqlalchemy import text
from werkzeug.utils import secure_filename
import os
import uuid
from models import users, Users

from werkzeug.security import check_password_hash, generate_password_hash
@app.get('/api/users')
def get_api_users():
    sql = text("SELECT user_id, UPPER(username) as username , 'true' as active ,image,role,email,created_at FROM Users")
    result = db.session.execute(sql).fetchall()
    rows = [dict(row._mapping) for row in result]
    if not rows:
        return jsonify({'message': 'No users found'})
    return jsonify(rows)

def fetch_user_by_id(user_id: int):
    sql = text("SELECT user_id, UPPER(username) as username , 'true' as active ,image,role,email,created_at FROM Users WHERE user_id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()
    if not result:
        return None
    return dict(result._mapping)

@app.get('/api/users/<int:user_id>')
def get_user_id(user_id: int):
    user = fetch_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'})
    return jsonify(user)

# -----------------------------
# Configuration
# -----------------------------
USERS_UPLOAD_FOLDER = 'static/images/users'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(USERS_UPLOAD_FOLDER, exist_ok=True)

app.config['USERS_UPLOAD_FOLDER'] = USERS_UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_email(email):
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# -----------------------------
# CREATE USER
# -----------------------------
@app.post('/api/users/create')
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    role = request.form.get('role')

    # Validation
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format', 'example': 'example@gmail.com'}), 400

    created_at = datetime.now()
    display_date = created_at.strftime("%d-%m-%Y")

    # Handle image upload
    image_url = None
    image_file = request.files.get('image')
    if image_file and allowed_file(image_file.filename):
        filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
        save_path = os.path.join(app.config['USERS_UPLOAD_FOLDER'], filename)
        image_file.save(save_path)
        image_url = f"/static/images/users/{filename}"  # URL for frontend

    # Insert user into DB
    new_user = Users(
        username=username,
        password=generate_password_hash(password),
        email=email,
        role=role,
        image=image_url,
        created_at=created_at
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': new_user.user_id,
            'username': new_user.username,
            'email': new_user.email,
            'role': new_user.role,
            'image': new_user.image,
            'created_at': display_date
        }
    }), 201

# -----------------------------
# UPDATE USER
# -----------------------------
@app.put('/api/users/update/<int:user_id>')
def update_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    role = request.form.get('role')

    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format', 'example': 'example@gmail.com'}), 400

    # Update fields
    user.username = username
    if password:
        user.password = generate_password_hash(password)
    user.email = email
    user.role = role

    # Handle image upload
    image_file = request.files.get('image')
    if image_file and allowed_file(image_file.filename):
        filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
        save_path = os.path.join(app.config['USERS_UPLOAD_FOLDER'], filename)
        image_file.save(save_path)
        user.image = f"/static/images/users/{filename}"

    db.session.commit()
    display_date = user.created_at.strftime("%d-%m-%Y")

    return jsonify({
        'message': 'User updated successfully',
        'user': {
            'id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'image': user.image,
            'created_at': display_date
        }
    })
@app.delete('/api/users/delete')
def delete_user():
    users = request.get_json()
    if not users or 'user_id' not in users:
        return {'error': 'user_id is required'}
    user_id = users['user_id']
    is_exists = fetch_user_by_id(user_id)
    if not is_exists:
        return {'message': 'User not found'}

    sql = text("DELETE FROM users WHERE user_id = :user_id")
    db.session.execute(sql, {"user_id": user_id})
    db.session.commit()

    return {
        'message': 'User deleted successfully',
        'deleted_user': is_exists
    }