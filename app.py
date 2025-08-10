from flask import Flask, render_template, request, redirect
from models import db, Agent, Ledger
from sqlalchemy import desc
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ledger.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    

    with app.app_context():
        from models import Agent, Ledger  # Ensure models are imported before creating tables
        db.create_all()

    return app
