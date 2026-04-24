# Car Insurance Data Migration Platform

An end-to-end data engineering project that simulates a real-world insurance data migration — from raw messy CSVs through a full ETL pipeline into a PostgreSQL database, exposed via a Flask REST API and visualized in an interactive analytics dashboard.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Manifests-326CE5?style=for-the-badge&logo=kubernetes)

---

## Project Journey

### Phase 1 — Data Generation (`generate_data.py`)

The first step was creating realistic synthetic data to simulate a real insurance company's database before migration.

Generated **5 raw CSV files** with intentional data quality issues:

| File | Rows | Description |
|---|---|---|
| `policyholders_raw.csv` | 3,060 | Customer demographics, credit scores, contact info |
| `vehicles_raw.csv` | 3,000 | Vehicle details, make, model, value |
| `policies_raw.csv` | 3,000 | Coverage type, premiums, start/end dates |
| `claims_raw.csv` | 2,050 | Claim amounts, types, fraud flags |
| `payments_raw.csv` | 3,500 | Payment history, late fees, methods |

The raw data was intentionally dirty — mixed date formats, inconsistent casing, currency strings, missing values, and duplicate rows — to simulate what a real migration looks like.

```bash
python generate_data.py
```

---

### Phase 2 — Data Cleaning / ETL (`process_data.py`)

Once the raw data was generated, it had to be cleaned before loading into the database.

**Data quality issues found and fixed:**

| Problem | Example | Fix Applied |
|---|---|---|
| Mixed date formats | `09 Sep 2023`, `02/05/2021`, `2024-10-25` | Parsed with `dateutil` |
| Inconsistent gender values | `M`, `male`, `MALE`, `Female` | Normalized → `Male / Female / Unknown` |
| Currency strings | `$68,642.11` vs `16600.15` | Stripped `$` and `,` |
| Boolean inconsistency | `Yes`, `TRUE`, `1` | Standardized to Python bool |
| Fuel type casing | `Diesel`, `DIESEL`, `diesel` | Title-cased |
| Duplicate rows | — | Removed with `drop_duplicates()` |
| Missing values | Phone 24%, credit score 8% | Filled or flagged |

**Raw vs Processed row counts after cleaning:**

| Table | Raw | Processed | Dropped |
|---|---|---|---|
| policyholders | 3,060 | 2,894 | 166 |
| vehicles | 3,000 | 3,000 | 0 |
| policies | 3,000 | 3,000 | 0 |
| claims | 2,050 | 2,000 | 50 |
| payments | 3,500 | 3,500 | 0 |

```bash
python process_data.py
```

---

### Phase 3 — Database Design (`models/`)

Designed a relational PostgreSQL schema using **SQLAlchemy ORM** with proper foreign key constraints.

```
policyholders
    └── vehicles       (policyholder_id → FK)
    └── policies       (policyholder_id → FK, vehicle_id → FK)
            └── claims     (policy_id → FK)
            └── payments   (policy_id → FK)
```

Each table has its own SQLAlchemy model in the `models/` folder:

- `models/policyholder.py` — customer details, credit score, demographics
- `models/vehicle.py` — make, model, year, value, fuel type
- `models/policy.py` — coverage type, premium, deductible, active status
- `models/claim.py` — claim amount, type, fraud flag, status
- `models/payment.py` — payment date, amount, late fee, method

---

### Phase 4 — Data Loading (`load_data.py`)

Loaded all 5 cleaned CSVs into PostgreSQL while respecting foreign key constraints — parent tables loaded before child tables.

```bash
python load_data.py
```

---

### Phase 5 — Containerization (`Dockerfile`, `docker-compose.yml`)

Containerized the full stack with Docker so the project runs consistently on any machine.

- **PostgreSQL 15** container as the database
- **Flask API** container as the backend
- Both containers connected on the same Docker network

```bash
docker compose up --build
```

---

### Phase 6 — REST API (`app/routes.py`)

Built a Flask REST API with 10 endpoints to query the migrated data:

| Endpoint | Description |
|---|---|
| `GET /` | API info and all available routes |
| `GET /summary` | Row counts for all 5 tables |
| `GET /policyholders/high-risk` | Customers with low credit or many prior claims |
| `GET /policyholders/high-risk/count` | Count of high-risk policyholders |
| `GET /claims/fraud` | All fraud-flagged claims |
| `GET /claims/summary` | Claims grouped by type with fraud analysis |
| `GET /policies/expiring-soon` | Policies expiring in the next 30 days |
| `GET /payments/late` | All late payments with fees |
| `GET /vehicles/<vehicle_id>` | Vehicle details by ID |
| `GET /migration/health` | Full system health check |

---

### Phase 7 — Analytics Dashboard (`dashboard.html`)

Built an interactive analytics dashboard served directly by Flask — no separate frontend server needed.

**Features:**
- Dark / Light theme toggle
- Sidebar navigation covering all API endpoints
- KPI cards — total policyholders, policies, claims, avg premium, avg credit score
- Claims by Type bar chart (total vs fraud)
- Fraud vs Legitimate donut chart
- Portfolio Risk Indicators with progress bars
- High Risk Policyholders table + chart by state
- Fraud Claims table with status badges
- Late Payments table with late fees
- Vehicle Lookup — search any vehicle by ID
- Migration Health — live row counts and system status

```
http://localhost:5000/dashboard
```

---

### Phase 8 — Kubernetes (`kubernetes/`)

Wrote production-ready Kubernetes manifests for deploying to any K8s cluster:

- `namespace.yaml` — isolated `carinsurance` namespace
- `postgres-deployment.yaml` + PersistentVolumeClaim — stateful DB
- `postgres-service.yaml` — ClusterIP service for internal DB access
- `flask-deployment.yaml` — 2 replicas of the Flask API
- `flask-service.yaml` — LoadBalancer exposing port 80

```bash
kubectl apply -f kubernetes/
```

---

### Phase 9 — Data Profiling Notebooks (`Notebooks/`)

Documented the data quality investigation and DB verification in Jupyter notebooks:

- **`data_profiling.ipynb`** — EDA on raw CSVs: missing values, distributions, inconsistencies
- **`PostgreSQL_data_load.ipynb`** — DB verification: row counts, sample queries, fraud by type, high-risk by state

---

## Running Locally

### Prerequisites
- Docker Desktop installed and running
- Python 3.10+

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/SahanaRamamurthy/CarInsurance-DataMigration_Platform.git
cd CarInsurance-DataMigration_Platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate raw data
python generate_data.py

# 4. Clean the data
python process_data.py

# 5. Start Docker containers
docker compose up --build

# 6. Load data into PostgreSQL
python load_data.py

# 7. Open the dashboard
# Visit: http://localhost:5000/dashboard
```

---

## Project Structure

```
CarInsurance-DataMigration-Platform/
│
├── Data/
│   ├── raw/                        # Raw CSVs with data quality issues
│   └── processed/                  # Cleaned CSVs after ETL
│
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── routes.py                   # All API endpoints
│   └── db.py                       # SQLAlchemy engine
│
├── models/                         # SQLAlchemy ORM models
│   ├── policyholder.py
│   ├── vehicle.py
│   ├── policy.py
│   ├── claim.py
│   └── payment.py
│
├── kubernetes/                     # K8s manifests
│   ├── namespace.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── flask-deployment.yaml
│   └── flask-service.yaml
│
├── Notebooks/
│   ├── data_profiling.ipynb
│   └── PostgreSQL_data_load.ipynb
│
├── generate_data.py                # Phase 1 — generate raw data
├── process_data.py                 # Phase 2 — ETL cleaning
├── load_data.py                    # Phase 4 — load into PostgreSQL
├── dashboard.html                  # Phase 7 — analytics dashboard
├── app.py                          # Flask entry point
├── docker-compose.yml              # Phase 5 — containerization
├── Dockerfile
├── Procfile                        # Render deployment
├── render.yaml                     # Render infrastructure config
└── requirements.txt
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Full PostgreSQL connection string (Render/Railway) | — |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | — |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `carinsurance_db` |
| `PORT` | Flask server port | `5000` |

---

## Author

**Sahana Ramamurthy**  
[GitHub](https://github.com/SahanaRamamurthy)
