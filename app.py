import json

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rent_home.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import models
import routes

@app.route("/")
@app.get("/login")
def login_page():
    return render_template("login.html")


@app.route("/properties")
def properties():
    return render_template("properties.html")

@app.route("/tenants")
def tenants():
    return render_template("tenants.html")
@app.route("/contracts")
def contracts():
    return render_template("contracts.html")
@app.route("/payments")
def payment():
    return render_template("payments.html")
@app.route("/maintenance")
def maintenance():
    return render_template("maintenance.html")
@app.route("/reports")
def reports():
    return render_template("reports.html")
@app.route("/users")
def users():
    return render_template("users.html")

if __name__ == "__main__":
    app.run(debug=True)