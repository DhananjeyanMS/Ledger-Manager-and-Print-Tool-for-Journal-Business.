# Flask application for Magazine Ledger Recorder


# Let's start with models.py (SQLite database)

from flask_sqlalchemy import SQLAlchemy
from datetime import date


db = SQLAlchemy()

class Agent(db.Model):
    __tablename__ = 'agent'
    agent_Code = db.Column(db.Integer, primary_key=True)
    agent_Name = db.Column(db.String(100), nullable=False)
    agent_Phonenumber = db.Column(db.String(15))
    agent_Address = db.Column(db.String(200))
    old_balance_Amount = db.Column(db.Float, default=0.00)
    area = db.Column(db.String(100), nullable=False, unique=True)  # Enforce unique area

class Ledger(db.Model):
    __tablename__ = 'ledger'
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=False)
    agent_Code = db.Column(db.Integer, db.ForeignKey('agent.agent_Code'), nullable=False)
    agent = db.relationship('Agent', backref=db.backref('ledgers', lazy=True))
    entry_date = db.Column(db.Date)
    ledger_type = db.Column(db.String(20), nullable=False)  # 'bill', 'receipt', or 'credit'

    # Financial fields
    bill_Amount = db.Column(db.Float, default=0.00)
    bill_date = db.Column(db.Date)
    receipt_Amount = db.Column(db.Float, default=0.00)
    receipt_date = db.Column(db.Date)
    credit_Amount = db.Column(db.Float, default=0.00)
    credit_date = db.Column(db.Date)
    old_balance_Amount = db.Column(db.Float, default=0.00)
    new_balance_Amount = db.Column(db.Float, default=0.00)

    # Distribution counts
    count_MM = db.Column(db.Integer, default=0)
    count_NS = db.Column(db.Integer, default=0)
    count_SV = db.Column(db.Integer, default=0)
    count_Valli = db.Column(db.Integer, default=0)
    count_Vani = db.Column(db.Integer, default=0)
    count_Azhagi = db.Column(db.Integer, default=0)
    count_Arasi = db.Column(db.Integer, default=0)
    count_Thriller = db.Column(db.Integer, default=0)

    ret_count_MM = db.Column(db.Integer, default=0)
    ret_count_NS = db.Column(db.Integer, default=0)
    ret_count_SV = db.Column(db.Integer, default=0)
    ret_count_Valli = db.Column(db.Integer, default=0)
    ret_count_Vani = db.Column(db.Integer, default=0)
    ret_count_Azhagi = db.Column(db.Integer, default=0)
    ret_count_Arasi = db.Column(db.Integer, default=0)
    ret_count_Thriller = db.Column(db.Integer, default=0)

    
    extras = db.Column(db.Float, default=0.00)
    Incentive = db.Column(db.Float, default=0.00)
    Transport = db.Column(db.Float, default=0.00)
    Postal_Courier = db.Column(db.Float, default=0.00)


# Continue with app.py and templates in next steps
