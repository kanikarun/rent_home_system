import json

from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rent_home.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'rent-home-secret-key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import models
import routes


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", endpoint="login")
@app.get("/login")
def login_page():
    return render_template("login.html")

@app.get("/dashboard")
@login_required
def dashboard():
    return render_template("index.html")

@app.route("/properties")
@login_required
def properties():
    return render_template("properties.html")

@app.route("/tenants")
@login_required
def tenants():
    return render_template("tenants.html")
@app.route("/contracts")
@login_required
def contracts():
    return render_template("contracts.html")
@app.route("/payments")
@login_required
def payment():
    return render_template("payments.html")
@app.route("/maintenance")
@login_required
def maintenance():
    return render_template("maintenance.html")
@app.route("/reports")
@login_required
def reports():
    return render_template("reports.html")
@app.route("/users")
@login_required
def users():
    return render_template("users.html")

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)