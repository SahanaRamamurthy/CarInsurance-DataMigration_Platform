# Car Insurance Data Migration Platform

An end-to-end data engineering project that simulates a real-world insurance data migration — from raw messy CSVs through a full ETL pipeline into a PostgreSQL database, exposed via a Flask REST API and visualized in an interactive analytics dashboard.

---

## Demo

> Dashboard: `http://localhost:5000/dashboard`

![Dashboard Preview](https://img.shields.io/badge/Dashboard-Dark%20%2F%20Light%20Theme-667eea?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)

---

## What This Project Does

| Stage | What Happens |
|---|---|
| **Generate** | Creates 5 realistic raw CSVs with intentional data quality issues |
| **Clean** | ETL pipeline fixes mixed date formats, inconsistent casing, currency strings, nulls |
| **Load** | Cleaned data is inserted into PostgreSQL with foreign key constraints |
| **Serve** | Flask REST API exposes 10 endpoints for querying the data |
| **Visualize** | Interactive dashboard displays fraud analysis, risk indicators, payment trends |

---

## Tech Stack

- **Python** — data generation, ETL pipeline, API
- **Pandas / NumPy** — data cleaning and transformation
- **PostgreSQL 15** — relational database with FK constraints
- **SQLAlchemy** — ORM and database models
- **Flask** — REST API with 10 endpoints
- **Flask-CORS** — cross-origin support
- **Docker & Docker Compose** — containerized deployment
- **Kubernetes** — production-ready manifests (namespace, deployments, services, PVC)
- **Chart.js** — interactive charts in the dashboard
- **Jupyter Notebooks** — data profiling and DB verification

---

## Project Structure

```
CarInsurance-DataMigration-Platform/
│
├── Data/
│   ├── raw/                    # Raw CSVs with data quality issues
│   └── processed/              # Cleaned CSVs after ETL
│
├── app/
│   ├── __init__.py             # Flask app factory
│   ├── routes.py               # All API endpoints
│   └── db.py                   # SQLAlchemy engine
│
├── models/                     # SQLAlchemy ORM models
│   ├── policyholder.py
│   ├── vehicle.py
│   ├── policy.py
│   ├── claim.py
│   └── payment.py
│
├── kubernetes/                 # K8s manifests
│   ├── namespace.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── flask-deployment.yaml
│   └── flask-service.yaml
│
├── Notebooks/
│   ├── data_profiling.ipynb        # EDA on raw data
│   └── PostgreSQL_data_load.ipynb  # DB verification queries
│
├── generate_data.py            # Generates raw synthetic CSVs
├── process_data.py             # ETL — cleans all 5 datasets
├── load_data.py                # Loads cleaned data into PostgreSQL
├── dashboard.html              # Full analytics dashboard (dark/light theme)
├── app.py                      # Entry point
├── docker-compose.yml
├── Dockerfile
├── Procfile                    # For Render deployment
├── render.yaml                 # Render infrastructure config
└── requirements.txt
```

---

## Data Model

Five tables with full relational integrity:

```
policyholders
    └── vehicles       (policyholder_id → FK)
    └── policies       (policyholder_id → FK, vehicle_id → FK)
            └── claims     (policy_id → FK)
            └── payments   (policy_id → FK)
```

---

## Data Quality Issues Handled

The raw CSVs intentionally contain real-world data problems that the ETL pipeline resolves:

| Issue | Example | Fix |
|---|---|---|
| Mixed date formats | `09 Sep 2023`, `02/05/2021`, `2024-10-25` | Parsed with `dateutil` |
| Inconsistent gender | `M`, `male`, `MALE`, `Female` | Normalized to `Male / Female / Unknown` |
| Currency strings | `$68,642.11` vs `16600.15` | Stripped `$` and `,` |
| Boolean inconsistency | `Yes`, `TRUE`, `1`, `true` | Standardized to Python bool |
| Fuel type casing | `Diesel`, `DIESEL`, `diesel` | Title-cased |
| Duplicate rows | — | Dropped with `drop_duplicates()` |
| Missing values | Phone (24%), credit score (8%) | Filled or flagged |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API info and all available routes |
| GET | `/summary` | Row counts for all 5 tables |
| GET | `/policyholders/high-risk` | Customers with low credit or many prior claims |
| GET | `/policyholders/high-risk/count` | Count of high-risk policyholders |
| GET | `/claims/fraud` | All fraud-flagged claims |
| GET | `/claims/summary` | Claims grouped by type with fraud analysis |
| GET | `/policies/expiring-soon` | Policies expiring in the next 30 days |
| GET | `/payments/late` | All late payments with fees |
| GET | `/vehicles/<vehicle_id>` | Vehicle details by ID |
| GET | `/migration/health` | Full system health check |
| GET | `/dashboard` | Interactive analytics dashboard |

---

## Running Locally

### Prerequisites
- Docker Desktop installed and running
- Python 3.10+

### 1. Clone the repo
```bash
git clone https://github.com/SahanaRamamurthy/CarInsurance-DataMigration_Platform.git
cd CarInsurance-DataMigration_Platform
```

### 2. Generate and clean the data
```bash
pip install -r requirements.txt
python generate_data.py
python process_data.py
```

### 3. Start Docker (PostgreSQL + Flask)
```bash
docker compose up --build
```

### 4. Load data into PostgreSQL
```bash
python load_data.py
```

### 5. Open the dashboard
```
http://localhost:5000/dashboard
```

---

## Dashboard Features

- **Dark / Light theme toggle**
- **KPI cards** — total policyholders, policies, claims, avg premium, avg credit score
- **Claims by Type** — bar chart (total vs fraud per category)
- **Fraud vs Legitimate** — donut chart
- **Portfolio Risk Indicators** — progress bars for high risk, fraud, late payments
- **High Risk Policyholders** — table + bar chart by state
- **Fraud Claims** — sortable table with status badges
- **Claims Summary** — full breakdown with avg amounts
- **Late Payments** — table with late fees
- **Vehicle Lookup** — search any vehicle by ID
- **Migration Health** — live row counts and system status

---

## Kubernetes Deployment

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/postgres-deployment.yaml
kubectl apply -f kubernetes/postgres-service.yaml
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl apply -f kubernetes/flask-service.yaml
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
