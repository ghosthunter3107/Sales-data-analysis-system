# 📊 Sales Data Analysis System (College Project)

A complete, beginner-friendly **Sales Data Analysis System** built with **Python, Flask, Pandas, MySQL, and Chart.js**. This web application provides end-to-end functionality to upload sales CSV files, inspect and sanitize dirty data, calculate critical retail business KPIs, render interactive visual charts, and persist records in a MySQL database.

---

## 🌟 Key Features

1. **Smart CSV Ingestion (`/upload`)**:
   - Supports drag-and-drop or file browsing for standard CSV files up to 16 MB.
   - Automatically detects and normalizes column aliases (e.g. `order id`, `unit_price`, `qty`, `sale_date`).
   - Generates an immediate preview of raw uploaded data with total row and column counts.
   - Includes 1-click **demo buttons** to load realistic sample datasets instantly.

2. **Automated Data Validation & Cleaning (`/validation`)**:
   - Detects missing cells, unparseable date strings, negative quantities, negative prices, and duplicate records.
   - Flags discrepancies where `Total_Sales` does not match `Quantity × Price`.
   - **Documented Cleaning Engine**: Standardizes dates to `YYYY-MM-DD`, recalculates missing or mismatched sales totals, removes unrecoverable bad rows, fills empty categories with `'General'`, and removes duplicates.
   - Displays a transparent before-and-after audit report.
   - Allows exporting the sanitized dataset as a clean CSV file.

3. **Sales Analysis Dashboard (`/dashboard`)**:
   - Displays 6 core business KPI cards:
     - **Total Revenue**: Sum of valid sales amounts ($\sum \text{Total\_Sales}$)
     - **Total Orders**: Count of unique order IDs ($\text{CountDistinct}(\text{Order\_ID})$)
     - **Total Units Sold**: Sum of physical quantities ($\sum \text{Quantity}$)
     - **Average Order Value (AOV)**: $\frac{\text{Total Revenue}}{\text{Total Orders}}$ (handles division by zero safely)
     - **Best-Selling Product**: Product with the highest volume of units sold
     - **Highest-Revenue Month**: Calendar month yielding peak revenue
   - Multi-dimensional filters: Filter dashboard metrics by **Date Range**, **Category**, and **Product**.
   - Performance breakdown tables for Categories and Top 10 Revenue-Generating Products.

4. **Interactive Visualizations (`/charts`)**:
   - Powered by **Chart.js**:
     - 📈 **Monthly Revenue Trend**: Smooth area/line chart of month-over-month performance.
     - 🍩 **Category-Wise Revenue Share**: Interactive donut chart showing departmental contribution.
     - 🏆 **Top 5 Products**: Dual-axis bar chart comparing units sold vs. revenue.
     - ⏱️ **Chronological Sales Velocity**: Daily transaction movement across the timeline.
     - 📦 **Department Volume**: Horizontal bar chart of physical inventory dispatched.

5. **MySQL Database Integration (`/database`)**:
   - Relational database schema with `products` and `sales` tables.
   - Safe parameterized queries (`PyMySQL`) preventing SQL injection.
   - Duplicate prevention (`INSERT IGNORE` on `order_id`).
   - Search by Order ID, Product name, or Category with pagination.
   - Graceful status reporting: If MySQL is not yet configured, the system operates in full preview mode without crashing.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Web Framework** | Python 3.10+ / Flask | Server-side routing, templates, API |
| **Data Processing & Cleaning** | Pandas & NumPy | CSV validation, audit engine, aggregations |
| **Database** | MySQL (PyMySQL) | Relational persistence & SQL queries |
| **Frontend UI** | HTML5, CSS3, Vanilla JS | Responsive, modern analytics design |
| **Charts & Visualizations** | Chart.js | Dynamic, interactive charts |
| **Testing** | pytest | Automated unit and integration testing |

---

## 📂 Project Structure

```text
sales management/
├── app.py                     # Main Flask application entry point
├── config.py                  # Environment loader & configuration
├── .env.example               # Example environment variables template
├── .env                       # Local environment settings (configure MySQL here)
├── requirements.txt           # Python dependencies
├── schema.sql                 # MySQL schema creation script
├── init_db.py                 # Terminal script to initialize MySQL database
├── README.md                  # Complete documentation and setup guide
│
├── core/
│   ├── __init__.py
│   ├── validator.py           # Pandas CSV validation and data cleaning engine
│   ├── analyzer.py            # Sales metric calculation & KPI formulas
│   ├── database.py            # MySQL connector, table creators & parameterized queries
│   └── data_store.py          # Session/memory dataset manager
│
├── routes/
│   ├── __init__.py
│   ├── main_routes.py         # Web page routes (Home, Upload, Validation, Dashboard, Charts, DB)
│   └── api_routes.py          # JSON API routes for dynamic filtering and charts
│
├── templates/
│   ├── base.html              # Base layout with responsive sidebar and header
│   ├── index.html             # Home introduction & system status page
│   ├── upload.html            # CSV upload & preview interface
│   ├── validation.html        # Data quality audit and cleaning report
│   ├── dashboard.html         # Sales KPI cards and breakdown tables
│   ├── charts.html            # Interactive Chart.js charts
│   ├── database.html          # MySQL records explorer and synchronization
│   ├── 404.html               # 404 error page
│   └── 500.html               # 500 error page
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern custom CSS styling
│   └── js/
│       ├── main.js            # UI interactions and drag-and-drop
│       └── charts.js          # Chart.js initialization and updates
│
├── sample_data/
│   ├── sample_sales.csv               # 60 clean realistic retail sales records
│   └── sample_sales_with_issues.csv   # Dirty test dataset (duplicates, bad dates, missing values)
│
└── tests/
    ├── __init__.py
    ├── test_validator.py      # Automated tests for data validation & cleaning
    ├── test_analyzer.py       # Automated tests for KPI formulas & calculations
    └── test_routes.py         # Automated tests for Flask routes & HTTP requests
```

---

## 🚀 Quick Start Guide (Run in 3 Steps)

### Step 1: Install Dependencies
Open your terminal (PowerShell or Command Prompt) in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Configure MySQL (Optional but Recommended)
Open the `.env` file in the project folder with any text editor and enter your MySQL root password:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_mysql_password
DB_NAME=sales_analysis
```

Run the database setup script to verify connection and create tables:
```bash
python init_db.py
```
> **Note**: If your MySQL password is not yet configured, you can still start the web server! The application will run smoothly in preview mode, and you can test CSV uploading, cleaning, dashboard KPIs, and charts.

### Step 3: Start the Application
Run the Flask server:
```bash
python app.py
```
Open your browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Running Automated Tests

Run the test suite to verify the validator, sales analytics formulas, and web routes:
```bash
python -m pytest -v
```
All 17 automated tests verify:
- Accurate column synonym mapping
- Detection of bad dates, negative numbers, and mismatched totals
- Data cleaning policy compliance
- KPI calculation formulas (Total Revenue, Orders, Units, AOV, Best Product, Peak Month)
- Safe division by zero on empty datasets
- HTTP endpoints and JSON chart APIs

---

## 📋 Complete Application Demonstration Workflow

When presenting this project in a college viva or evaluation, follow these steps:

1. **Start on the Home Page (`/`)**:
   - Point out the clean UI, the technology stack badge, and the live MySQL status indicator.
2. **Click "Upload CSV" (`/upload`)**:
   - Demonstrate drag-and-drop file upload, or click **"⚡ Try Demo Dataset"** (loads `sample_sales.csv`).
   - Click **"🧪 Test Dirty Data Validation"** (loads `sample_sales_with_issues.csv`) to show anomaly handling!
3. **Inspect the Data Validation Page (`/validation`)**:
   - Show how the audit detects duplicate rows, missing prices, negative quantities, bad date formats, and mismatched sales totals.
   - Click **"Sanitize & Clean Data Now"**.
   - Show the before-and-after report explaining exactly what was cleaned and why.
4. **Explore the Sales Dashboard (`/dashboard`)**:
   - Point out the 6 KPI cards (Total Revenue, Orders, Units Sold, Average Order Value, Best-Selling Product, and Highest-Revenue Month).
   - Use the **Category** and **Date Range** filters to show how metrics re-calculate dynamically.
5. **View the Interactive Charts (`/charts`)**:
   - Show the monthly revenue line chart, category revenue donut chart, and top 5 products comparison.
   - Hover over chart segments to display formatted currency tooltips.
6. **Save to MySQL Database (`/database`)**:
   - Click **"Save Active Cleaned Records to MySQL"**.
   - Show the saved records in the table explorer, filter by category, and perform searches by Order ID or Product name.

---

## 🎓 College Viva / Academic Questions & Answers

### Q1: How does the system handle missing or mismatched `Total_Sales`?
> If `Total_Sales` is missing or does not equal `Quantity × Price`, the validator automatically recalculates it using the formula:
> $$\text{Total\_Sales} = \text{Quantity} \times \text{Price}$$
> Any adjustments are logged and displayed to the user in the transparent cleaning report.

### Q2: How does the application avoid division by zero when calculating Average Order Value?
> In `core/analyzer.py`, the calculation checks if `total_orders > 0`:
> ```python
> avg_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0
> ```
> This prevents server crashes when an empty or heavily filtered dataset has 0 orders.

### Q3: How is duplicate data handled in MySQL?
> In `core/database.py`, transactions are stored using:
> ```sql
> INSERT IGNORE INTO sales (order_id, product_name, category, sale_date, quantity, unit_price, total_sales, region)
> VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
> ```
> Because `order_id` has a unique constraint, re-uploading an existing dataset skips duplicate records safely without raising a database crash.

### Q4: Why use Flask and Chart.js rather than heavy frameworks?
> Flask provides a lightweight, modular Python architecture that directly communicates with Pandas data structures without complex middleware. Chart.js provides hardware-accelerated HTML5 canvas charts that update interactively with zero build-step overhead.
