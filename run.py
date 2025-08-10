# run.py

from app import create_app
from flask import Flask, render_template, request, redirect, jsonify, url_for, make_response
from models import db, Agent, Ledger
from sqlalchemy import desc, extract, func
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = create_app()


@app.route('/')
def home():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    try:
        agents = Agent.query.all()
        total_agents = len(agents)
        # Get month/year from query params
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        now = datetime.now()
        current_month = month if month else now.month
        current_year = year if year else now.year
        if total_agents == 0:
            return render_template('dashboard.html', 
                                 agents=[],
                                 monthly_stats={},
                                 total_agents=0,
                                 total_monthly_receipts=0.0,
                                 total_monthly_credits=0.0,
                                 total_monthly_bills=0.0,
                                 total_net_sales=0.0,
                                 recent_entries=[],
                                 current_month=current_month,
                                 current_year=current_year,
                                 agent_metrics=[],
                                 monthwise_metrics=[],
                                 chart_data={},
                                 total_balance=0.0,
                                 total_extras=0.0,
                                 total_transport=0.0,
                                 total_incentive=0.0,
                                 total_postal=0.0)
        # --- Agent-wise metrics ---
        agent_metrics = []
        total_balance = 0.0
        total_extras = 0.0
        total_transport = 0.0
        total_incentive = 0.0
        total_postal = 0.0
        for agent in agents:
            # Current month
            bills = db.session.query(func.sum(Ledger.bill_Amount)).filter_by(area=agent.area, ledger_type='bill').filter(
                extract('month', Ledger.bill_date) == current_month,
                extract('year', Ledger.bill_date) == current_year).scalar() or 0.0
            receipts = db.session.query(func.sum(Ledger.receipt_Amount)).filter_by(area=agent.area, ledger_type='receipt').filter(
                extract('month', Ledger.entry_date) == current_month,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            credits = db.session.query(func.sum(Ledger.credit_Amount)).filter_by(area=agent.area, ledger_type='credit').filter(
                extract('month', Ledger.entry_date) == current_month,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            extras = db.session.query(func.sum(Ledger.extras)).filter_by(area=agent.area).filter(
                extract('month', Ledger.entry_date) == current_month,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            transport = db.session.query(func.sum(Ledger.Transport)).filter_by(area=agent.area).filter(
                extract('month', Ledger.entry_date) == current_month,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            incentive = db.session.query(func.sum(Ledger.Incentive)).filter_by(area=agent.area).filter(
                extract('month', Ledger.entry_date) == current_month,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            postal = db.session.query(func.sum(Ledger.Postal_Courier)).filter_by(area=agent.area).filter(
                extract('month', Ledger.entry_date) == current_month,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            # Last month
            if current_month == 1:
                last_month = 12
                last_year = current_year - 1
            else:
                last_month = current_month - 1
                last_year = current_year
            last_bills = db.session.query(func.sum(Ledger.bill_Amount)).filter_by(area=agent.area, ledger_type='bill').filter(
                extract('month', Ledger.bill_date) == last_month,
                extract('year', Ledger.bill_date) == last_year).scalar() or 0.0
            # Percentage improvement
            percent_improve = ((bills - last_bills) / last_bills * 100) if last_bills else 0.0
            # Latest new_balance_Amount for agent
            latest_bill = db.session.query(Ledger).filter_by(area=agent.area, ledger_type='bill').order_by(Ledger.bill_date.desc()).first()
            new_balance = latest_bill.new_balance_Amount if latest_bill else 0.0
            total_balance += new_balance
            total_extras += extras
            total_transport += transport
            total_incentive += incentive
            total_postal += postal
            agent_metrics.append({
                'agent_name': agent.agent_Name,
                'area': agent.area,
                'bills': bills,
                'receipts': receipts,
                'credits': credits,
                'extras': extras,
                'transport': transport,
                'incentive': incentive,
                'postal': postal,
                'new_balance': new_balance,
                'percent_improve': percent_improve
            })
        # --- Monthwise metrics for line graphs ---
        monthwise_metrics = []
        chart_labels = []
        sales_data = []
        credit_data = []
        receipt_data = []
        extras_data = []
        transport_data = []
        incentive_data = []
        postal_data = []
        for i in range(1, 13):
            month_label = datetime(current_year, i, 1).strftime('%b')
            chart_labels.append(month_label)
            month_bills = db.session.query(func.sum(Ledger.bill_Amount)).filter(
                extract('month', Ledger.bill_date) == i,
                extract('year', Ledger.bill_date) == current_year).scalar() or 0.0
            month_credits = db.session.query(func.sum(Ledger.credit_Amount)).filter(
                extract('month', Ledger.entry_date) == i,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            month_receipts = db.session.query(func.sum(Ledger.receipt_Amount)).filter(
                extract('month', Ledger.entry_date) == i,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            month_extras = db.session.query(func.sum(Ledger.extras)).filter(
                extract('month', Ledger.entry_date) == i,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            month_transport = db.session.query(func.sum(Ledger.Transport)).filter(
                extract('month', Ledger.entry_date) == i,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            month_incentive = db.session.query(func.sum(Ledger.Incentive)).filter(
                extract('month', Ledger.entry_date) == i,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            month_postal = db.session.query(func.sum(Ledger.Postal_Courier)).filter(
                extract('month', Ledger.entry_date) == i,
                extract('year', Ledger.entry_date) == current_year).scalar() or 0.0
            monthwise_metrics.append({
                'month': month_label,
                'bills': month_bills,
                'credits': month_credits,
                'receipts': month_receipts,
                'extras': month_extras,
                'transport': month_transport,
                'incentive': month_incentive,
                'postal': month_postal
            })
            sales_data.append(month_bills)
            credit_data.append(month_credits)
            receipt_data.append(month_receipts)
            extras_data.append(month_extras)
            transport_data.append(month_transport)
            incentive_data.append(month_incentive)
            postal_data.append(month_postal)
        # --- Agent-wise line graph data ---
        agent_chart_data = {}
        for agent in agents:
            agent_sales = []
            agent_credits = []
            agent_receipts = []
            for i in range(1, 13):
                agent_sales.append(db.session.query(func.sum(Ledger.bill_Amount)).filter_by(area=agent.area, ledger_type='bill').filter(
                    extract('month', Ledger.bill_date) == i,
                    extract('year', Ledger.bill_date) == current_year).scalar() or 0.0)
                agent_credits.append(db.session.query(func.sum(Ledger.credit_Amount)).filter_by(area=agent.area, ledger_type='credit').filter(
                    extract('month', Ledger.entry_date) == i,
                    extract('year', Ledger.entry_date) == current_year).scalar() or 0.0)
                agent_receipts.append(db.session.query(func.sum(Ledger.receipt_Amount)).filter_by(area=agent.area, ledger_type='receipt').filter(
                    extract('month', Ledger.entry_date) == i,
                    extract('year', Ledger.entry_date) == current_year).scalar() or 0.0)
            agent_chart_data[agent.agent_Name] = {
                'sales': agent_sales,
                'credits': agent_credits,
                'receipts': agent_receipts
            }
        chart_data = {
            'labels': chart_labels,
            'sales': sales_data,
            'credits': credit_data,
            'receipts': receipt_data,
            'extras': extras_data,
            'transport': transport_data,
            'incentive': incentive_data,
            'postal': postal_data,
            'agent_chart_data': agent_chart_data
        }
        # --- Old metrics for compatibility ---
        monthly_stats = {}
        for agent in agents:
            total_receipts = db.session.query(db.func.sum(Ledger.receipt_Amount)).filter_by(
                area=agent.area, ledger_type='receipt'
            ).filter(
                extract('month', Ledger.entry_date) == current_month,
                extract('year', Ledger.entry_date) == current_year
            ).scalar() or 0.0
            total_credits = db.session.query(db.func.sum(Ledger.credit_Amount)).filter_by(
                area=agent.area, ledger_type='credit'
            ).filter(
                extract('month', Ledger.entry_date) == current_month,
                extract('year', Ledger.entry_date) == current_year
            ).scalar() or 0.0
            total_bills = db.session.query(db.func.sum(Ledger.bill_Amount)).filter_by(
                area=agent.area, ledger_type='bill'
            ).filter(
                extract('month', Ledger.bill_date) == current_month,
                extract('year', Ledger.bill_date) == current_year
            ).scalar() or 0.0
            monthly_stats[agent.area] = {
                'agent_name': agent.agent_Name,
                'total_receipts': float(total_receipts),
                'total_credits': float(total_credits),
                'total_bills': float(total_bills),
                'net_sales': float(total_bills - total_receipts - total_credits)
            }
        total_monthly_receipts = sum(stats['total_receipts'] for stats in monthly_stats.values())
        total_monthly_credits = sum(stats['total_credits'] for stats in monthly_stats.values())
        total_monthly_bills = sum(stats['total_bills'] for stats in monthly_stats.values())
        total_net_sales = sum(stats['net_sales'] for stats in monthly_stats.values())
        recent_entries = db.session.query(Ledger).filter(
            Ledger.entry_date.isnot(None)
        ).order_by(Ledger.entry_date.desc()).limit(10).all()
        return render_template('dashboard.html', 
                             agents=agents,
                             monthly_stats=monthly_stats,
                             total_agents=total_agents,
                             total_monthly_receipts=total_monthly_receipts,
                             total_monthly_credits=total_monthly_credits,
                             total_monthly_bills=total_monthly_bills,
                             total_net_sales=total_net_sales,
                             recent_entries=recent_entries,
                             current_month=current_month,
                             current_year=current_year,
                             agent_metrics=agent_metrics,
                             monthwise_metrics=monthwise_metrics,
                             chart_data=chart_data,
                             total_balance=total_balance,
                             total_extras=total_extras,
                             total_transport=total_transport,
                             total_incentive=total_incentive,
                             total_postal=total_postal)
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0  # or None, depending on your logic
    
def safe_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Assuming your date format is 'YYYY-MM-DD'
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None  # or handle error as needed

@app.route('/add_agent', methods=['GET', 'POST'])
def add_agent():
    message = None
    success = False
    if request.method == 'POST':
        agent_code = request.form['agent_Code']
        area = request.form['area']
        # Check for unique agent code
        if Agent.query.filter_by(agent_Code=agent_code).first():
            message = 'Agent code already exists. Please use a unique code.'
        # Check for unique area
        elif Agent.query.filter_by(area=area).first():
            message = 'Area is already assigned to another agent. Please use a unique area.'
        else:
            agent = Agent(
                agent_Code=agent_code,
                agent_Name=request.form['agent_name'],
                agent_Phonenumber=request.form['phone'],
                agent_Address=request.form['address'],
                old_balance_Amount=float(request.form['opening_balance'] or 0),
                area=area
            )
            db.session.add(agent)
            db.session.commit()
            message = 'Agent added successfully!'
            success = True
    return render_template('agent.html', message=message, success=success)

from flask import request, render_template, redirect, jsonify
import json

# Helper to get month and year from a date

def get_month_year(date):
    return date.month, date.year if date else (None, None)

@app.route('/add_receipt', methods=['GET', 'POST'])
def add_receipt():
    agents = Agent.query.all()
    agent_data = [
        {
            'area': agent.area,
            'agent_Name': agent.agent_Name,
            'agent_Code': agent.agent_Code,
            'old_balance': safe_float(agent.old_balance_Amount or 0)
        } for agent in agents
    ]
    message = None
    success = False
    if request.method == 'POST':
        area = request.form['area']
        agent = Agent.query.filter_by(area=area).first()
        entry_date = parse_date(request.form['entry_date'])
        receipt_date = parse_date(request.form['receipt_date'])
        bill_exists = (
            Ledger.query
            .filter_by(area=area, ledger_type='bill')
            .order_by(Ledger.bill_date.desc())  # Most recent first
            .first()
        )

        if bill_exists:
            bill_month = bill_exists.bill_date.month
            bill_year = bill_exists.bill_date.year
            if (
                entry_date and receipt_date and
                (
                    (entry_date.year < bill_year) or
                    (entry_date.year == bill_year and entry_date.month < bill_month)
                ) and
                (
                    (receipt_date.year < bill_year) or
                    (receipt_date.year == bill_year and receipt_date.month < bill_month)
                )
            ):
                message = "Cannot add receipt - Bill already exists. Choose different date and try again"
                success = False
        else:
            ledger = Ledger(
                area=area,
                agent_Code=agent.agent_Code,
                agent=agent,
                entry_date=entry_date,
                receipt_date=parse_date(request.form['receipt_date']),
                receipt_Amount=safe_float(request.form.get('receipt_Amount', 0)),
                old_balance_Amount=safe_float(request.form.get('old_balance', 0)),
                ledger_type='receipt'
            )
            db.session.add(ledger)
            db.session.commit()
            message = 'Receipt entry added successfully!'
            success = True
    return render_template('add_receipt.html', agents=agents, agent_data=agent_data, message=message, success=success)

@app.route('/list_receipts', methods=['GET'])
def list_receipts():
    area = request.args.get('area')
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    query = Ledger.query.filter_by(area=area, ledger_type='receipt')
    if month and year:
        query = query.filter(extract('month', Ledger.entry_date) == month, extract('year', Ledger.entry_date) == year)
    receipts = query.order_by(Ledger.entry_date.desc()).all()
        # Get latest bill for the area (for lock check)
    latest_bill = (
        Ledger.query
        .filter_by(area=area, ledger_type='bill')
        .order_by(Ledger.bill_date.desc())
        .first()
    )

    bill_month = latest_bill.bill_date.month if latest_bill else None
    bill_year = latest_bill.bill_date.year if latest_bill else None
    result = []
    for r in receipts:
        editable = True
        if latest_bill and r.entry_date:
            if (r.entry_date and r.receipt_date and ((r.entry_date.year < bill_year) or (r.entry_date.year == bill_year and r.entry_date.month < bill_month)) and ((r.receipt_date.year < bill_year) or (r.receipt_date.year == bill_year and r.receipt_date.month < bill_month))):
                editable = False
        result.append({
            'id': r.id,
            'entry_date': r.entry_date.strftime('%Y-%m-%d') if r.entry_date else '',
            'receipt_date': r.receipt_date.strftime('%Y-%m-%d') if r.receipt_date else '',
            'receipt_Amount': r.receipt_Amount,
            'agent_code': r.agent_Code,
            'agent_name': r.agent.agent_Name if r.agent else '',
            'editable': editable,
            'deletable': editable
        })
    return jsonify(result)

@app.route('/edit_receipt/<int:receipt_id>', methods=['GET', 'POST'])
def edit_receipt(receipt_id):
    receipt = Ledger.query.get_or_404(receipt_id)
    # Restriction: can edit only if no bill exists for this agent/area/month (bill_date is when bill was created)
    # If bill was created in month X, it locks receipts/credits from month X-1
    next_month = receipt.entry_date.month + 1 if receipt.entry_date.month < 12 else 1
    next_year = receipt.entry_date.year if receipt.entry_date.month < 12 else receipt.entry_date.year + 1
    editable = True
    latest_bill = (
        Ledger.query
        .filter_by(area=receipt.area, ledger_type='bill')
        .order_by(Ledger.bill_date.desc())
        .first()
    )
    if latest_bill:
        bill_month = latest_bill.bill_date.month if latest_bill else None
        bill_year = latest_bill.bill_date.year if latest_bill else None
        if (receipt.entry_date and receipt.receipt_date and ((receipt.entry_date.year < bill_year) or (receipt.entry_date.year == bill_year and receipt.entry_date.month < bill_month)) and ((receipt.receipt_date.year < bill_year) or (receipt.receipt_date.year == bill_year and receipt.receipt_date.month < bill_month))):
            editable = False
    if request.method == 'POST' and editable:
        receipt.entry_date = parse_date(request.form.get('entry_date'))
        receipt.receipt_date = parse_date(request.form.get('receipt_date'))
        receipt.receipt_Amount = safe_float(request.form.get('receipt_Amount'))
        db.session.commit()
        return jsonify({'success': True})
    # For GET, return data for pre-filling the form
    return jsonify({
        'id': receipt.id,
        'area': receipt.area,
        'agent_code': receipt.agent_Code,
        'agent_name': receipt.agent.agent_Name if receipt.agent else '',
        'entry_date': receipt.entry_date.strftime('%Y-%m-%d') if receipt.entry_date else '',
        'receipt_date': receipt.receipt_date.strftime('%Y-%m-%d') if receipt.receipt_date else '',
        'receipt_Amount': receipt.receipt_Amount,
        'editable': editable
    })

@app.route('/delete_receipt/<int:receipt_id>', methods=['POST'])
def delete_receipt(receipt_id):
    receipt = Ledger.query.get_or_404(receipt_id)
    # Restriction: can delete only if no bill exists for this agent/area/month (bill_date is when bill was created)
    # If bill was created in month X, it locks receipts/credits from month X-1
    latest_bill = (
        Ledger.query
        .filter_by(area=receipt.area, ledger_type='bill')
        .order_by(Ledger.bill_date.desc())
        .first()
    )
    bill_month = latest_bill.bill_date.month if latest_bill else None
    bill_year = latest_bill.bill_date.year if latest_bill else None
    editable = True
    if latest_bill and receipt.entry_date:
        if (receipt.entry_date and receipt.receipt_date and ((receipt.entry_date.year < bill_year) or (receipt.entry_date.year == bill_year and receipt.entry_date.month < bill_month)) and ((receipt.receipt_date.year < bill_year) or (receipt.receipt_date.year == bill_year and receipt.receipt_date.month < bill_month))):
            editable = False

    if editable:
        db.session.delete(receipt)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Cannot delete: Bill already exists for this agent/area/month.'})


@app.route('/add_credit', methods=['GET', 'POST'])
def add_credit():
    agents = Agent.query.all()
    agent_data = [
        {
            'area': agent.area,
            'agent_Name': agent.agent_Name,
            'agent_Code': agent.agent_Code,
            'old_balance': safe_float(agent.old_balance_Amount or 0)
        } for agent in agents
    ]
    
    # Check for success message from edit redirect
    if request.method == 'GET':
        success = request.args.get('success') == 'true'
        message = request.args.get('message')
        if success and message:
            return render_template('add_credit.html', agents=agents, agent_data=agent_data, message=message, success=success)
    
    message = None
    success = False
    if request.method == 'POST':
        area = request.form['area']
        agent = Agent.query.filter_by(area=area).first()
        entry_date = parse_date(request.form['entry_date'])
        credit_date = parse_date(request.form['credit_date'])        
        latest_bill = (
            Ledger.query
            .filter_by(area=area, ledger_type='bill')
            .order_by(Ledger.bill_date.desc())
            .first()
        )

        if latest_bill:
            bill_month = latest_bill.bill_date.month
            bill_year = latest_bill.bill_date.year
            if (
                entry_date and credit_date and
                (
                    (entry_date.year < bill_year) or
                    (entry_date.year == bill_year and entry_date.month < bill_month)
                ) and
                (
                    (credit_date.year < bill_year) or
                    (credit_date.year == bill_year and credit_date.month < bill_month)
                )
            ):
                message = "Cannot add credit - Bill already exists. Choose different date and try again"
                success = False
      

        else:
            ledger = Ledger(
                area=area,
                agent_Code=agent.agent_Code,
                agent=agent,
                entry_date=entry_date,
                credit_date=parse_date(request.form['credit_date']),
                ret_count_MM=safe_int(request.form.get('ret_count_MM', 0)),
                ret_count_NS=safe_int(request.form.get('ret_count_NS', 0)),
                ret_count_SV=safe_int(request.form.get('ret_count_SV', 0)),
                ret_count_Valli=safe_int(request.form.get('ret_count_Valli', 0)),
                ret_count_Vani=safe_int(request.form.get('ret_count_Vani', 0)),
                ret_count_Azhagi=safe_int(request.form.get('ret_count_Azhagi', 0)),
                ret_count_Arasi=safe_int(request.form.get('ret_count_Arasi', 0)),
                ret_count_Thriller=safe_int(request.form.get('ret_count_Thriller', 0)),
                extras=safe_float(request.form.get('extras', 0)),
                Incentive=safe_float(request.form.get('Incentive', 0)),
                Transport=safe_float(request.form.get('Transport', 0)),
                Postal_Courier=safe_float(request.form.get('Postal_Courier', 0)),
                credit_Amount=safe_float(request.form.get('credit_Amount', 0)),
                old_balance_Amount=safe_float(request.form.get('old_balance', 0)),
                ledger_type='credit'
            )
            db.session.add(ledger)
            db.session.commit()
            message = 'Credit entry added successfully!'
            success = True
    return render_template('add_credit.html', agents=agents, agent_data=agent_data, message=message, success=success)

@app.route('/list_credits', methods=['GET'])
def list_credits():
    area = request.args.get('area')
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    query = Ledger.query.filter_by(area=area, ledger_type='credit')
    if month and year:
        query = query.filter(extract('month', Ledger.entry_date) == month, extract('year', Ledger.entry_date) == year)
    credits = query.order_by(Ledger.entry_date.desc()).all()
    result = []
    for c in credits:
        # If bill was created in month X, it locks receipts/credits from month X-1
        latest_bill = (
            Ledger.query
            .filter_by(area=c.area, ledger_type='bill')
            .order_by(Ledger.bill_date.desc())
            .first()
        )

        editable = True
        if latest_bill:
            bill_month = latest_bill.bill_date.month
            bill_year = latest_bill.bill_date.year

            if (
                (c.entry_date and ((c.entry_date.year < bill_year) or
                                (c.entry_date.year == bill_year and c.entry_date.month < bill_month)))
                or
                (c.credit_date and ((c.credit_date.year < bill_year) or
                                    (c.credit_date.year == bill_year and c.credit_date.month < bill_month)))
            ):
                editable = False
        result.append({
            'id': c.id,
            'entry_date': c.entry_date.strftime('%Y-%m-%d') if c.entry_date else '',
            'credit_date': c.credit_date.strftime('%Y-%m-%d') if c.credit_date else '',
            'credit_Amount': c.credit_Amount,
            'agent_code': c.agent_Code,
            'agent_name': c.agent.agent_Name if c.agent else '',
            'editable': editable,
            'deletable': editable
        })
    return jsonify(result)

@app.route('/edit_credit/<int:credit_id>', methods=['GET', 'POST'])
def edit_credit(credit_id):
    credit = Ledger.query.get_or_404(credit_id)
    # If bill was created in month X, it locks receipts/credits from month X-1
    latest_bill = (
        Ledger.query
        .filter_by(area=credit.area, ledger_type='bill')
        .order_by(Ledger.bill_date.desc())
        .first()
    )

    editable = True
    if latest_bill:
        bill_month = latest_bill.bill_date.month
        bill_year = latest_bill.bill_date.year

        if (
            (credit.entry_date and ((credit.entry_date.year < bill_year) or
                                    (credit.entry_date.year == bill_year and credit.entry_date.month < bill_month)))
            or
            (credit.credit_date and ((credit.credit_date.year < bill_year) or
                                    (credit.credit_date.year == bill_year and credit.credit_date.month < bill_month)))
        ):
            editable = False
    
    if request.method == 'POST' and editable:
        credit.entry_date = parse_date(request.form.get('entry_date'))
        credit.credit_date = parse_date(request.form.get('credit_date'))
        credit.credit_Amount = safe_float(request.form.get('credit_Amount'))
        # Update return counts and other fields as needed
        credit.ret_count_MM = safe_int(request.form.get('ret_count_MM', 0))
        credit.ret_count_NS = safe_int(request.form.get('ret_count_NS', 0))
        credit.ret_count_SV = safe_int(request.form.get('ret_count_SV', 0))
        credit.ret_count_Valli = safe_int(request.form.get('ret_count_Valli', 0))
        credit.ret_count_Vani = safe_int(request.form.get('ret_count_Vani', 0))
        credit.ret_count_Azhagi = safe_int(request.form.get('ret_count_Azhagi', 0))
        credit.ret_count_Arasi = safe_int(request.form.get('ret_count_Arasi', 0))
        credit.ret_count_Thriller = safe_int(request.form.get('ret_count_Thriller', 0))
        credit.extras = safe_float(request.form.get('extras', 0))
        credit.Incentive = safe_float(request.form.get('Incentive', 0))
        credit.Transport = safe_float(request.form.get('Transport', 0))
        credit.Postal_Courier = safe_float(request.form.get('Postal_Courier', 0))
        db.session.commit()
        return redirect('/add_credit?success=true&message=Credit entry updated successfully!')
    
    # For GET requests (AJAX calls from edit button), return JSON
    return jsonify({
        'id': credit.id,
        'area': credit.area,
        'agent_code': credit.agent_Code,
        'agent_name': credit.agent.agent_Name if credit.agent else '',
        'entry_date': credit.entry_date.strftime('%Y-%m-%d') if credit.entry_date else '',
        'credit_date': credit.credit_date.strftime('%Y-%m-%d') if credit.credit_date else '',
        'credit_Amount': credit.credit_Amount,
        'ret_count_MM': credit.ret_count_MM,
        'ret_count_NS': credit.ret_count_NS,
        'ret_count_SV': credit.ret_count_SV,
        'ret_count_Valli': credit.ret_count_Valli,
        'ret_count_Vani': credit.ret_count_Vani,
        'ret_count_Azhagi': credit.ret_count_Azhagi,
        'ret_count_Arasi': credit.ret_count_Arasi,
        'ret_count_Thriller': credit.ret_count_Thriller,
        'extras': credit.extras,
        'Incentive': credit.Incentive,
        'Transport': credit.Transport,
        'Postal_Courier': credit.Postal_Courier,
        'editable': editable
    })

@app.route('/delete_credit/<int:credit_id>', methods=['POST'])
def delete_credit(credit_id):
    credit = Ledger.query.get_or_404(credit_id)
    # If bill was created in month X, it locks receipts/credits from month X-1
    latest_bill = (
        Ledger.query
        .filter_by(area=credit.area, ledger_type='bill')
        .order_by(Ledger.bill_date.desc())
        .first()
    )

    editable = True
    if latest_bill:
        bill_month = latest_bill.bill_date.month
        bill_year = latest_bill.bill_date.year

        if (
            (credit.entry_date and ((credit.entry_date.year < bill_year) or
                                    (credit.entry_date.year == bill_year and credit.entry_date.month < bill_month)))
            or
            (credit.credit_date and ((credit.credit_date.year < bill_year) or
                                    (credit.credit_date.year == bill_year and credit.credit_date.month < bill_month)))
        ):
            editable = False

    if editable:
        db.session.delete(credit)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Cannot delete: Bill already exists for this agent/area/month.'})

@app.route('/add_bill', methods=['GET', 'POST'])
def add_bill():
    agents = Agent.query.all()
    agent_data = [
        {
            'area': agent.area,
            'agent_Name': agent.agent_Name,
            'agent_Code': agent.agent_Code,
            'old_balance': safe_float(agent.old_balance_Amount or 0)
        } for agent in agents
    ]
    
    # Check for success message from edit redirect
    if request.method == 'GET':
        success = request.args.get('success') == 'true'
        message = request.args.get('message')
        if success and message:
            return render_template('add_bill.html', agents=agents, agent_data=agent_data, message=message, success=success)
    
    message = None
    success = False
    if request.method == 'POST':
        area = request.form['area']
        agent = Agent.query.filter_by(area=area).first()
        entry_date = parse_date(request.form['entry_date'])
        month = entry_date.month
        year = entry_date.year
        # Check if a bill already exists for this agent/area/month (using bill_date)
        bill_exists = Ledger.query.filter_by(area=area, ledger_type='bill').filter(
            extract('month', Ledger.bill_date) == month,
            extract('year', Ledger.bill_date) == year
        ).first()
        if bill_exists:
            message = 'Cannot add bill: Bill already exists for this agent/area/month.'
        else:
            # Calculate bill and new balance here as needed
            # bill_Amount = safe_float(request.form.get('bill_Amount', 0))
            # old_balance = safe_float(request.form.get('old_balance', 0))
            # last_bill = Ledger.query.filter_by(area=area, ledger_type='bill') \
            #     .order_by(Ledger.bill_date.desc()) \
            #     .first()

            # if last_bill:
            #     start_date = last_bill.bill_date
            # else:
            #     # If no previous bill, start from earliest possible date
            #     start_date = None

            # end_date = parse_date(request.form['bill_date'])

            # Build base queries
            # receipts_query = db.session.query(db.func.sum(Ledger.receipt_Amount)) \
            #     .filter_by(area=area, ledger_type='receipt')

            # credits_query = db.session.query(db.func.sum(Ledger.credit_Amount)) \
            #     .filter_by(area=area, ledger_type='credit')

            # Apply date filtering
            # if start_date:
            #     receipts_query = receipts_query.filter(Ledger.entry_date > start_date, Ledger.entry_date <= end_date)
            #     credits_query = credits_query.filter(Ledger.entry_date > start_date, Ledger.entry_date <= end_date)
            # else:
            #     receipts_query = receipts_query.filter(Ledger.entry_date <= end_date)
            #     credits_query = credits_query.filter(Ledger.entry_date <= end_date)

            # total_receipts = receipts_query.scalar() or 0.0
            # total_credits = credits_query.scalar() or 0.0
            # new_balance = old_balance + bill_Amount - total_receipts - total_credits
            ledger = Ledger(
                area=area,
                agent_Code=agent.agent_Code,
                agent=agent,
                entry_date=entry_date,
                bill_date=parse_date(request.form['bill_date']),
                count_MM=safe_int(request.form.get('count_MM', 0)),
                count_NS=safe_int(request.form.get('count_NS', 0)),
                count_SV=safe_int(request.form.get('count_SV', 0)),
                count_Valli=safe_int(request.form.get('count_Valli', 0)),
                count_Vani=safe_int(request.form.get('count_Vani', 0)),
                count_Azhagi=safe_int(request.form.get('count_Azhagi', 0)),
                count_Arasi=safe_int(request.form.get('count_Arasi', 0)),
                count_Thriller=safe_int(request.form.get('count_Thriller', 0)),
                bill_Amount=(request.form.get('bill_Amount', 0)),
                old_balance_Amount=(request.form.get('old_balance', 0)),
                new_balance_Amount=(request.form.get('new_balance', 0)),
                ledger_type='bill'
            )
            db.session.add(ledger)
            # Update agent's old_balance_Amount for next month
            agent.old_balance_Amount = (request.form.get('new_balance', 0))
            db.session.commit()
            message = 'Bill entry added successfully!'
            success = True
    return render_template('add_bill.html', agents=agents, agent_data=agent_data, message=message, success=success)

from sqlalchemy import func

@app.route('/list_bills', methods=['GET'])
def list_bills():
    area = request.args.get('area')
    query = Ledger.query.filter_by(area=area, ledger_type='bill').order_by(Ledger.entry_date.desc())
    bills = query.all()
    result = []
    for b in bills:
        # Only the most recent bill is editable
        latest_bill = Ledger.query.filter_by(area=b.area, ledger_type='bill').order_by(Ledger.entry_date.desc()).first()
        result.append({
            'id': b.id,
            'entry_date': b.entry_date.strftime('%Y-%m-%d') if b.entry_date else '',
            'bill_date': b.bill_date.strftime('%Y-%m-%d') if b.bill_date else '',
            'bill_Amount': b.bill_Amount,
            'agent_code': b.agent_Code,
            'agent_name': b.agent.agent_Name if b.agent else '',
            'editable': latest_bill and latest_bill.id == b.id,
            'deletable': False
        })
    return jsonify(result)

@app.route('/get_monthly_totals', methods=['GET'])
def get_monthly_totals():
    area = request.args.get('area')
    bill_date_str = request.args.get('bill_date')  # from query string
    if not area or not bill_date_str:
        return jsonify({'total_receipts': 0, 'total_credits': 0})

    bill_date = parse_date(bill_date_str)  # convert to datetime.date

    # Find the last bill before the current bill date
    last_bill = (
        Ledger.query
        .filter(Ledger.area == area, Ledger.ledger_type == 'bill', Ledger.bill_date < bill_date)
        .order_by(Ledger.bill_date.desc())
        .first()
    )

    # Set start_date as that bill's date (if exists)
    start_date = last_bill.bill_date if last_bill else None
    end_date = bill_date

    # Build base queries
    receipts_query = db.session.query(db.func.sum(Ledger.receipt_Amount)) \
        .filter(Ledger.area == area, Ledger.ledger_type == 'receipt')

    credits_query = db.session.query(db.func.sum(Ledger.credit_Amount)) \
        .filter(Ledger.area == area, Ledger.ledger_type == 'credit')

    # Apply date filtering
    if start_date:
        receipts_query = receipts_query.filter(Ledger.entry_date > start_date, Ledger.entry_date <= end_date)
        credits_query = credits_query.filter(Ledger.entry_date > start_date, Ledger.entry_date <= end_date)
    else:
        receipts_query = receipts_query.filter(Ledger.entry_date <= end_date)
        credits_query = credits_query.filter(Ledger.entry_date <= end_date)

    total_receipts = receipts_query.scalar() or 0.0
    total_credits = credits_query.scalar() or 0.0

    return jsonify({
        'total_receipts': float(total_receipts),
        'total_credits': float(total_credits)
    })



@app.route('/edit_bill/<int:bill_id>', methods=['GET', 'POST'])
def edit_bill(bill_id):
    bill = Ledger.query.get_or_404(bill_id)
    latest_bill = Ledger.query.filter_by(area=bill.area, ledger_type='bill').order_by(Ledger.entry_date.desc()).first()
    
    if request.method == 'POST' and latest_bill and latest_bill.id == bill.id:
        bill.entry_date = parse_date(request.form.get('entry_date'))
        bill.bill_date = parse_date(request.form.get('bill_date'))
        bill.bill_Amount = safe_float(request.form.get('bill_Amount'))
        bill.count_MM = safe_int(request.form.get('count_MM', 0))
        bill.count_NS = safe_int(request.form.get('count_NS', 0))
        bill.count_SV = safe_int(request.form.get('count_SV', 0))
        bill.count_Valli = safe_int(request.form.get('count_Valli', 0))
        bill.count_Vani = safe_int(request.form.get('count_Vani', 0))
        bill.count_Azhagi = safe_int(request.form.get('count_Azhagi', 0))
        bill.count_Arasi = safe_int(request.form.get('count_Arasi', 0))
        bill.count_Thriller = safe_int(request.form.get('count_Thriller', 0))
        db.session.commit()
        return redirect('/add_bill?success=true&message=Bill entry updated successfully!')
    
    # For GET requests (AJAX calls from edit button), return JSON
    return jsonify({
        'id': bill.id,
        'area': bill.area,
        'agent_code': bill.agent_Code,
        'agent_name': bill.agent.agent_Name if bill.agent else '',
        'old_balance': bill.old_balance_Amount,
        'entry_date': bill.entry_date.strftime('%Y-%m-%d') if bill.entry_date else '',
        'bill_date': bill.bill_date.strftime('%Y-%m-%d') if bill.bill_date else '',
        'bill_Amount': bill.bill_Amount,
        'count_MM': bill.count_MM,
        'count_NS': bill.count_NS,
        'count_SV': bill.count_SV,
        'count_Valli': bill.count_Valli,
        'count_Vani': bill.count_Vani,
        'count_Azhagi': bill.count_Azhagi,
        'count_Arasi': bill.count_Arasi,
        'count_Thriller': bill.count_Thriller,
        'editable': latest_bill and latest_bill.id == bill.id
    })

@app.route('/view_ledger')
def view_ledger():
    ledgers = Ledger.query.order_by(Ledger.entry_date.desc()).all()
    return render_template('view_ledger.html', ledgers=ledgers)

@app.route('/print_bill/<int:ledger_id>')
def print_bill(ledger_id):
    ledger = Ledger.query.get_or_404(ledger_id)
    agent = Agent.query.filter_by(agent_Code=ledger.agent_Code).first()

    return render_template('bill_template.html', ledger=ledger, agent=agent)


@app.route('/print', methods=['GET'])
def print_page():
    agents = Agent.query.order_by(Agent.agent_Name).all()
    return render_template('print.html', agents=agents)

@app.route('/print_docs', methods=['GET'])
def print_docs():
    agent_code = request.args.get('agent_code', 'all')
    # Get selected month/year from query params, default to current
    try:
        selected_month = int(request.args.get('month', None))
        selected_year = int(request.args.get('year', None))
    except (TypeError, ValueError):
        selected_month = None
        selected_year = None
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    if not selected_month:
        selected_month = current_month
    if not selected_year:
        selected_year = current_year
    # Calculate previous month/year
    if selected_month == 1:
        prev_month = 12
        prev_year = selected_year - 1
    else:
        prev_month = selected_month - 1
        prev_year = selected_year

    # Get agents
    if agent_code == 'all':
        agents = Agent.query.order_by(Agent.agent_Name).all()
    else:
        agents = Agent.query.filter_by(agent_Code=int(agent_code)).all()

    rendered_blocks = []
    for agent in agents:
        # Bills (for selected month/year)
        bills = Ledger.query.filter_by(area=agent.area, ledger_type='bill').filter(
            extract('month', Ledger.bill_date) == selected_month,
            extract('year', Ledger.bill_date) == selected_year
        ).order_by(Ledger.bill_date.asc()).all()
        for bill in bills:
            rendered_blocks.append(render_template('bill_print.html', ledger=bill, agent=agent))
        # Credits (for previous month/year)
        credits = Ledger.query.filter_by(area=agent.area, ledger_type='credit').filter(
            extract('month', Ledger.entry_date) == prev_month,
            extract('year', Ledger.entry_date) == prev_year
        ).order_by(Ledger.entry_date.asc()).all()
        for credit in credits:
            rendered_blocks.append(render_template('credit_print.html', ledger=credit, agent=agent))
        # Receipts (for previous month/year)
        receipts = Ledger.query.filter_by(area=agent.area, ledger_type='receipt').filter(
            extract('month', Ledger.entry_date) == prev_month,
            extract('year', Ledger.entry_date) == prev_year
        ).order_by(Ledger.entry_date.asc()).all()
        for receipt in receipts:
            rendered_blocks.append(render_template('receipt_print.html', ledger=receipt, agent=agent))

    # Wrap all blocks in a print wrapper and auto-trigger print
    html = render_template('print_docs_wrapper.html', blocks=rendered_blocks)
    response = make_response(html)
    return response


if __name__ == '__main__':
    app.run(debug=True)
