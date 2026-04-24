import os
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "carinsurance_db")

print(f"DB_USER: {DB_USER}")
print(f"DB_HOST: {DB_HOST}")
print(f"DB_PORT: {DB_PORT}")
print(f"DB_NAME: {DB_NAME}")
print(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS policyholders (
    policyholder_id     VARCHAR(20) PRIMARY KEY,
    full_name           VARCHAR(100) NOT NULL,
    date_of_birth       DATE,
    age                 INTEGER,
    gender              VARCHAR(10),
    state               VARCHAR(5),
    phone               VARCHAR(15),
    email               VARCHAR(100),
    license_years       INTEGER,
    prior_claims_count  INTEGER,
    credit_score        INTEGER,
    marital_status      VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id          VARCHAR(20) PRIMARY KEY,
    policyholder_id     VARCHAR(20) REFERENCES policyholders(policyholder_id),
    make                VARCHAR(50),
    model               VARCHAR(50),
    year                INTEGER,
    color               VARCHAR(30),
    vehicle_value_usd   NUMERIC(12,2),
    mileage             INTEGER,
    fuel_type           VARCHAR(20),
    vin                 VARCHAR(30),
    is_modified         BOOLEAN
);

CREATE TABLE IF NOT EXISTS policies (
    policy_id           VARCHAR(20) PRIMARY KEY,
    policyholder_id     VARCHAR(20) REFERENCES policyholders(policyholder_id),
    vehicle_id          VARCHAR(20) REFERENCES vehicles(vehicle_id),
    coverage_type       VARCHAR(50),
    start_date          DATE,
    end_date            DATE,
    premium_usd         NUMERIC(10,2),
    deductible_usd      NUMERIC(10,2),
    is_active           BOOLEAN,
    agent_id            VARCHAR(20),
    coverage_amount_usd NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id            VARCHAR(20) PRIMARY KEY,
    policy_id           VARCHAR(20) REFERENCES policies(policy_id),
    claim_date          DATE,
    claim_type          VARCHAR(50),
    claim_amount_usd    NUMERIC(12,2),
    settled_amount_usd  NUMERIC(12,2),
    status              VARCHAR(30),
    description         TEXT,
    is_fraud_flag       BOOLEAN,
    days_to_report      INTEGER
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id          VARCHAR(20) PRIMARY KEY,
    policy_id           VARCHAR(20) REFERENCES policies(policy_id),
    payment_date        DATE,
    amount_usd          NUMERIC(10,2),
    payment_method      VARCHAR(30),
    status              VARCHAR(20),
    is_late             BOOLEAN,
    late_fee_usd        NUMERIC(8,2)
);
"""

PROCESSED = "Data/processed"

# Load order respects foreign key dependencies
LOAD_ORDER = [
    ("policyholders", "policyholders.csv"),
    ("vehicles",      "vehicles.csv"),
    ("policies",      "policies.csv"),
    ("claims",        "claims.csv"),
    ("payments",      "payments.csv"),
]

with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
    print("Database connection successful!")

# Drop in reverse foreign-key order, then recreate
with engine.begin() as conn:
    conn.execute(text("""
        DROP TABLE IF EXISTS payments CASCADE;
        DROP TABLE IF EXISTS claims CASCADE;
        DROP TABLE IF EXISTS policies CASCADE;
        DROP TABLE IF EXISTS vehicles CASCADE;
        DROP TABLE IF EXISTS policyholders CASCADE;
    """))
    conn.execute(text(CREATE_TABLES))

# Load policyholders first, then filter child tables to valid IDs
ph = pd.read_csv(os.path.join(PROCESSED, "policyholders.csv"))
valid_ph_ids = set(ph["policyholder_id"])

vehicles = pd.read_csv(os.path.join(PROCESSED, "vehicles.csv"))
vehicles = vehicles[vehicles["policyholder_id"].isin(valid_ph_ids)]

policies = pd.read_csv(os.path.join(PROCESSED, "policies.csv"))
policies = policies[policies["policyholder_id"].isin(valid_ph_ids)]
policies = policies[policies["vehicle_id"].isin(set(vehicles["vehicle_id"]))]

valid_policy_ids = set(policies["policy_id"])

claims = pd.read_csv(os.path.join(PROCESSED, "claims.csv"))
claims = claims[claims["policy_id"].isin(valid_policy_ids)]

payments = pd.read_csv(os.path.join(PROCESSED, "payments.csv"))
payments = payments[payments["policy_id"].isin(valid_policy_ids)]

tables = [
    ("policyholders", ph),
    ("vehicles",      vehicles),
    ("policies",      policies),
    ("claims",        claims),
    ("payments",      payments),
]

for table, df in tables:
    df.to_sql(table, engine, if_exists="append", index=False,
              method="multi", chunksize=500)
    print(f"  Loaded {table}: {len(df)} rows")

print("Data loaded successfully!")
