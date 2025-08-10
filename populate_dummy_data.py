from app import create_app
from models import db, Agent, Ledger
from datetime import date, timedelta, datetime
import random

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create 10 agents
    agents = []
    for i in range(10):
        agent = Agent(
            agent_Code=1000 + i,
            agent_Name=f'Agent {i+1}',
            agent_Phonenumber=f'90000000{str(i+1).zfill(2)}',
            agent_Address=f'Address {i+1}',
            old_balance_Amount=random.uniform(0, 1000),
            area=f'Area {i+1}'
        )
        agents.append(agent)
    db.session.add_all(agents)
    db.session.commit()

    today = date.today()
    start_year = 2025
    start_month = 1
    end_year = today.year
    end_month = today.month

    for agent in agents:
        old_balance = agent.old_balance_Amount
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if year == end_year and month > end_month:
                    break
                # Bill (one per month)
                bill_day = min(5, (date(year, month, 1) + timedelta(days=27)).day)
                bill_entry_date = date(year, month, bill_day)
                bill_Amount = random.uniform(1000, 5000)
                # Receipts (1-2 per month)
                for _ in range(random.randint(1, 2)):
                    receipt_day = random.randint(1, 28)
                    receipt_entry_date = date(year, month, receipt_day)
                    receipt = Ledger(
                        area=agent.area,
                        agent_Code=agent.agent_Code,
                        agent=agent,
                        entry_date=receipt_entry_date,
                        receipt_date=receipt_entry_date,
                        receipt_Amount=random.uniform(500, 2000),
                        old_balance_Amount=old_balance,
                        ledger_type='receipt'
                    )
                    db.session.add(receipt)
                # Credits (1-2 per month)
                for _ in range(random.randint(1, 2)):
                    credit_day = random.randint(1, 28)
                    credit_entry_date = date(year, month, credit_day)
                    credit = Ledger(
                        area=agent.area,
                        agent_Code=agent.agent_Code,
                        agent=agent,
                        entry_date=credit_entry_date,
                        credit_date=credit_entry_date,
                        ret_count_MM=random.randint(0, 10),
                        ret_count_NS=random.randint(0, 10),
                        ret_count_SV=random.randint(0, 10),
                        ret_count_Valli=random.randint(0, 10),
                        ret_count_Vani=random.randint(0, 10),
                        ret_count_Azhagi=random.randint(0, 10),
                        ret_count_Arasi=random.randint(0, 10),
                        ret_count_Thriller=random.randint(0, 10),
                        extras=random.uniform(0, 100),
                        Incentive=random.uniform(0, 50),
                        Transport=random.uniform(0, 50),
                        Postal_Courier=random.uniform(0, 50),
                        credit_Amount=random.uniform(100, 1000),
                        old_balance_Amount=old_balance,
                        ledger_type='credit'
                    )
                    db.session.add(credit)
                # Bill (after receipts/credits)
                bill = Ledger(
                    area=agent.area,
                    agent_Code=agent.agent_Code,
                    agent=agent,
                    entry_date=bill_entry_date,
                    bill_date=bill_entry_date,
                    count_MM=random.randint(10, 50),
                    count_NS=random.randint(10, 50),
                    count_SV=random.randint(10, 50),
                    count_Valli=random.randint(10, 50),
                    count_Vani=random.randint(10, 50),
                    count_Azhagi=random.randint(10, 50),
                    count_Arasi=random.randint(10, 50),
                    count_Thriller=random.randint(10, 50),
                    bill_Amount=bill_Amount,
                    old_balance_Amount=old_balance,
                    new_balance_Amount=old_balance + bill_Amount - random.uniform(500, 2000) - random.uniform(100, 1000),
                    ledger_type='bill'
                )
                db.session.add(bill)
                old_balance = bill.new_balance_Amount
    db.session.commit()
    print('Dummy data for 10 agents, every month from Jan 2025 to today, populated.') 