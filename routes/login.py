from flask import render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash
from models import Users
from app import app


@app.post("/login")
def login_action():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"})

    user = Users.query.filter_by(username=username).first()

    if not user:
        return jsonify({"success": False, "error": "User not found"})

    if not check_password_hash(user.password, password):
        return jsonify({"success": False, "error": "Incorrect password"})

    # Save session

    session["user_id"] = user.user_id
    session["username"] = user.username
    session["role"] = user.role

    return jsonify({"success": True})

