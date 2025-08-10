# 📒 Ledger Management & Dashboard System

A **Flask-based ledger management application** for tracking receipts, credits, and performance of agents across different areas, complete with **custom bill/receipt/credit print generation**.  
Designed for small to medium businesses that need a simple yet robust accounting tool with business-specific templates and locking rules for accounting integrity.

---

## 📌 Features

- **Agent Management**
  - Add agents.
  - View detailed agent performance history.

- **Ledger Entries**
  - Record **Receipts** and **Credits** with dates, amounts, and remarks.
  - Edit or delete entries **only if** the month is not locked by a bill.

- **Dashboard**
  - Aggregated metrics for the current month and overall totals.
  - Agent-wise monthly performance.
  - Interactive charts for:
    - Monthly totals.
    - Agent contribution trends.

- **Bill Locking**
  - If a bill exists for a given month and area, that month becomes **read-only**.
  - Ensures accounting integrity.

- **Custom Print Generation**
  - Generate **Bills**, **Receipts**, and **Credit Notes** using a **business-branded template**.
  - Automatically populated with ledger data (agent, date, area, amounts, remarks).
  - Print-friendly output for direct printing or PDF export.
  - Bulk bill generation for all agents in a given month.

- **View complete ledger**
  - Pagination & filtering for large datasets.
---

## 🛠 Tech Stack

- **Backend:** Python 3, Flask, SQLAlchemy
- **Frontend:** HTML, Bootstrap, JavaScript (Chart.js)
- **Database:** SQLite (can be swapped for PostgreSQL/MySQL)
- **Date Handling:** Python `datetime`

---

## 📂 Project Structure

```

.
├── app.py                  # Flask application factory
├── run.py                  # Main entry point with routes
├── models.py               # SQLAlchemy models (Agent, Ledger)
├── templates/              # HTML templates (Jinja2)
│   ├── dashboard.html
│   ├── bill\_template.html     # Print template for bills
│   ├── receipt\_template.html  # Print template for receipts
│   ├── credit\_template.html   # Print template for credits
│   └── ...
├── static/                 # CSS, JS, Chart.js assets, and print styles
├── requirements.txt        # Dependencies
└── README.md               # Project documentation

````

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ Install dependencies

### 4️⃣ Initialize the database

```bash
flask shell
>>> from app import db, create_app
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     exit()
```

### 5️⃣ Run the server

```bash
flask --app run.py run
```

App will be available at:
📍 `http://127.0.0.1:5000`

---

## 📊 Dashboard Details

The main dashboard (`/`) displays:

* **Total receipts and credits** for the current month.
* **Agent-wise breakdown** with receipt and credit totals.
* **Monthly performance chart** (sum of receipts and credits).
* **Agent performance chart** (stacked totals by agent per month).

Data is aggregated server-side for faster page loads.

---

## ✏️ CRUD Operations

| Entity  | Add | Edit | Delete | Lock Rules                                  |
| ------- | --- | ---- | ------ | ------------------------------------------- |
| Agent   | ✅   | ✅    | ✅      | No locks                                    |
| Receipt | ✅   | ✅    | ✅      | Locked if bill exists for that month & area |
| Credit  | ✅   | ✅    | ✅      | Locked if bill exists for that month & area |

---

## 🔒 Bill Locking Logic

Before updating or deleting a ledger entry:

* Check if **any** `Ledger` entry exists with:

  * `type = "Bill"`
  * `area` matches the entry
  * `date` in the same month/year
* If such a bill exists → modification is **denied**.

This ensures past months cannot be altered once billed.

---

## 🖨 Printing & Document Generation

The system supports **direct print previews** for:

* **Bills** — generated for a given month & area.
* **Receipts** — acknowledging payment from agents.
* **Credits** — documenting credits issued.

**Process:**

1. User clicks "Print" from dashboard or ledger entry.
2. Flask route fetches relevant data from the database.
3. Data is inserted into a **custom HTML template** styled with your business branding.
4. The document is optimized for printing or PDF export.
5. The user can print directly or share the PDF via email/messaging.

## 🧩 Future Improvements

* Authentication & role-based access control.
* Export reports as PDF/Excel directly from dashboard.
* Automatic database backups.
* Mobile-friendly dashboard layout.

## 👨‍💻 Author

Developed by **\[Dhananjeyan M S]**
📧 [msdhanan98@gmail.com](mailto:msdhanan98@example.com)
🌐 [Portfolio](https://unimad.notion.site/Dhananjeyan-M-S-e9b2328ee41c4acdae01421360580e76)

