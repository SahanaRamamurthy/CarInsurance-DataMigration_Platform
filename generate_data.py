import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(99)
random.seed(99)

NUM_POLICYHOLDERS = 3000
NUM_VEHICLES      = 3000
NUM_POLICIES      = 3000
NUM_CLAIMS        = 2000
NUM_PAYMENTS      = 3500

# ── Reference pools ────────────────────────────────────────────────────────────
first_names = ["James","Maria","David","Sarah","Michael","Emma","John","Lisa",
               "Robert","Anna","Chris","Priya","Kevin","Fatima","Daniel","Yuki",
               "Carlos","Aisha","Tom","Nina","Raj","Zoe","Mark","Elena","Sam"]
last_names  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller",
               "Davis","Wilson","Moore","Taylor","Anderson","Thomas","Jackson",
               "White","Harris","Martin","Thompson","Robinson","Clark"]

car_makes = {
    "Toyota":   ["Camry","Corolla","RAV4","Prius","Highlander"],
    "Honda":    ["Civic","Accord","CR-V","Pilot","Fit"],
    "Ford":     ["F-150","Mustang","Explorer","Escape","Focus"],
    "BMW":      ["3 Series","5 Series","X3","X5","M3"],
    "Mercedes": ["C-Class","E-Class","GLE","A-Class","S-Class"],
    "Chevrolet":["Silverado","Malibu","Equinox","Tahoe","Spark"],
    "Audi":     ["A4","A6","Q5","Q7","TT"],
    "Hyundai":  ["Elantra","Tucson","Santa Fe","Sonata","Kona"],
    "Nissan":   ["Altima","Rogue","Sentra","Pathfinder","Leaf"],
    "Tesla":    ["Model 3","Model S","Model X","Model Y","Cybertruck"],
}
coverage_types  = ["Comprehensive", "Third Party", "Third Party Fire & Theft", "Collision"]
claim_types     = ["Accident", "Theft", "Natural Disaster", "Vandalism", "Fire", "Flood"]
claim_statuses  = ["Approved", "Rejected", "Pending", "Under Review", "Settled"]
payment_methods = ["Credit Card", "Bank Transfer", "Direct Debit", "Cheque", "Cash"]
states          = ["CA","NY","TX","FL","IL","PA","OH","GA","NC","MI",
                   "NJ","VA","WA","AZ","MA","TN","IN","MO","MD","WI"]

def random_date(start_year=2018, end_year=2024):
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def messy_date(dt):
    fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d %b %Y"])
    return dt.strftime(fmt)

def messy_bool():
    return random.choice(["Yes", "No", "yes", "no", "Y", "N", "1", "0", "TRUE", "FALSE", True, False])

# ── 1. POLICYHOLDERS ───────────────────────────────────────────────────────────
ph_ids = [f"PH{str(i).zfill(5)}" for i in range(1, NUM_POLICYHOLDERS + 1)]
policyholders_raw = []

for pid in ph_ids:
    dob = random_date(1955, 2000)
    age = 2024 - dob.year

    # Mess 1: some names missing or ALL CAPS
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    if random.random() < 0.04:
        name = None
    elif random.random() < 0.15:
        name = name.upper()

    # Mess 2: gender inconsistent
    gender = random.choice(["Male","Female","M","F","male","female","MALE","FEMALE","m","f"])

    # Mess 3: phone number formats mixed
    phone_num = f"{random.randint(200,999)}{random.randint(1000000,9999999)}"
    fmt = random.randint(0, 3)
    if fmt == 0:   phone = f"+1-{phone_num[:3]}-{phone_num[3:6]}-{phone_num[6:]}"
    elif fmt == 1: phone = f"({phone_num[:3]}) {phone_num[3:6]}-{phone_num[6:]}"
    elif fmt == 2: phone = phone_num
    else:          phone = None

    # Mess 4: license years sometimes negative or 0
    license_years = random.randint(1, 35)
    if random.random() < 0.03:
        license_years = -random.randint(1, 5)

    policyholders_raw.append({
        "policyholder_id":    pid,
        "full_name":          name,
        "date_of_birth":      messy_date(dob) if random.random() > 0.03 else None,
        "age":                age,
        "gender":             gender,
        "state":              random.choice(states),
        "phone":              phone,
        "email":              f"{random.choice(first_names).lower()}{random.randint(1,999)}@{random.choice(['gmail.com','yahoo.com','outlook.com','hotmail.com'])}",
        "license_years":      license_years,
        "prior_claims_count": int(np.random.choice([0,1,2,3,4], p=[0.50,0.25,0.13,0.08,0.04])),
        "credit_score":       int(np.clip(np.random.normal(680, 80), 300, 850)) if random.random() > 0.08 else None,
        "marital_status":     random.choice(["Single","Married","Divorced","Widowed","single","married","S","M"]),
    })

# ── 2. VEHICLES ────────────────────────────────────────────────────────────────
vehicle_ids = [f"VH{str(i).zfill(5)}" for i in range(1, NUM_VEHICLES + 1)]
vehicles_raw = []

for i, vid in enumerate(vehicle_ids):
    make  = random.choice(list(car_makes.keys()))
    model = random.choice(car_makes[make])
    year  = random.randint(2000, 2024)
    value = round(random.uniform(3000, 120000), 2)

    # Mess 5: vehicle value stored as string with currency symbol
    if random.random() > 0.4:
        value_str = f"${value:,.2f}"
    else:
        value_str = str(value)
    if random.random() < 0.04:
        value_str = None

    # Mess 6: mileage missing or unrealistically high
    mileage = random.randint(0, 200000)
    if random.random() < 0.03:
        mileage = random.randint(500000, 999999)  # bad data
    if random.random() < 0.05:
        mileage = None

    vehicles_raw.append({
        "vehicle_id":        vid,
        "policyholder_id":   ph_ids[i % NUM_POLICYHOLDERS],
        "make":              make,
        "model":             model,
        "year":              year,
        "color":             random.choice(["Red","Blue","Black","White","Silver","Grey","Green","Yellow","Orange","gray","white","BLACK"]),
        "vehicle_value_usd": value_str,
        "mileage":           mileage,
        "fuel_type":         random.choice(["Petrol","Diesel","Electric","Hybrid","petrol","DIESEL","EV","hybrid"]),
        "vin":               ''.join(random.choices('ABCDEFGHJKLMNPRSTUVWXYZ0123456789', k=17)),
        "is_modified":       messy_bool(),
    })

# ── 3. POLICIES ────────────────────────────────────────────────────────────────
policy_ids = [f"POL{str(i).zfill(5)}" for i in range(1, NUM_POLICIES + 1)]
policies_raw = []

for i, polid in enumerate(policy_ids):
    start_date   = random_date(2019, 2024)
    end_date     = start_date + timedelta(days=365)
    coverage     = random.choice(coverage_types)
    premium      = round(random.uniform(300, 5000), 2)

    # Mess 7: premium as string with currency
    if random.random() < 0.3:
        premium_str = f"${premium}"
    else:
        premium_str = str(premium)

    # Mess 8: some end dates BEFORE start dates
    if random.random() < 0.02:
        end_date = start_date - timedelta(days=random.randint(1, 30))

    policies_raw.append({
        "policy_id":       polid,
        "policyholder_id": ph_ids[i % NUM_POLICYHOLDERS],
        "vehicle_id":      vehicle_ids[i % NUM_VEHICLES],
        "coverage_type":   coverage if random.random() > 0.1 else coverage.lower(),
        "start_date":      messy_date(start_date),
        "end_date":        messy_date(end_date),
        "premium_usd":     premium_str,
        "deductible_usd":  round(random.uniform(200, 2000), 2) if random.random() > 0.1 else None,
        "is_active":       messy_bool(),
        "agent_id":        f"AGT{random.randint(1,50):03d}",
        "coverage_amount_usd": round(random.uniform(10000, 500000), 2),
    })

# ── 4. CLAIMS ──────────────────────────────────────────────────────────────────
claim_ids = [f"CLM{str(i).zfill(5)}" for i in range(1, NUM_CLAIMS + 1)]
claims_raw = []

for clid in claim_ids:
    policy_id    = random.choice(policy_ids)
    claim_date   = random_date(2020, 2024)
    claim_amount = round(random.uniform(500, 80000), 2)
    status       = random.choice(claim_statuses)

    # Mess 9: claim amount sometimes 0 or negative (bad entry)
    if random.random() < 0.03:
        claim_amount = 0
    if random.random() < 0.02:
        claim_amount = -round(random.uniform(100, 5000), 2)

    # Mess 10: settlement amount > claim amount (illogical)
    settled_amount = round(claim_amount * random.uniform(0.5, 1.0), 2)
    if random.random() < 0.04:
        settled_amount = round(claim_amount * random.uniform(1.1, 1.5), 2)

    # Fraud signals: ~8% base rate, slightly higher for very large claims
    is_fraud_signal = random.random() < (0.12 if claim_amount > 50000 else 0.06)

    claims_raw.append({
        "claim_id":           clid,
        "policy_id":          policy_id,
        "claim_date":         messy_date(claim_date),
        "claim_type":         random.choice(claim_types),
        "claim_amount_usd":   claim_amount,
        "settled_amount_usd": settled_amount if status == "Settled" else None,
        "status":             status,
        "description":        random.choice([
            "Front end collision on highway",
            "Rear end damage in parking lot",
            "Vehicle stolen from residential area",
            "Flood damage during heavy rainfall",
            "Windshield cracked by debris",
            "Hit and run incident",
            "Fire damage in garage",
            "Vandalism - scratches and dents",
            None
        ]),
        "is_fraud_flag":      "Yes" if is_fraud_signal else "No",
        "days_to_report":     random.randint(0, 60) if random.random() > 0.05 else None,
    })

# ── 5. PAYMENTS ────────────────────────────────────────────────────────────────
payment_ids = [f"PAY{str(i).zfill(5)}" for i in range(1, NUM_PAYMENTS + 1)]
payments_raw = []

for payid in payment_ids:
    policy_id    = random.choice(policy_ids)
    pay_date     = random_date(2019, 2024)
    amount       = round(random.uniform(100, 5000), 2)
    method       = random.choice(payment_methods)

    # Mess 11: payment status inconsistent values
    status = random.choice(["Paid","Failed","Pending","paid","PAID","failed","SUCCESS","success","Overdue","overdue"])

    # Mess 12: some amounts as strings
    amount_val = f"${amount}" if random.random() < 0.2 else amount

    payments_raw.append({
        "payment_id":    payid,
        "policy_id":     policy_id,
        "payment_date":  messy_date(pay_date) if random.random() > 0.04 else None,
        "amount_usd":    amount_val,
        "payment_method":method,
        "status":        status,
        "is_late":       "Yes" if random.random() < 0.15 else "No",
        "late_fee_usd":  round(random.uniform(10, 100), 2) if random.random() < 0.2 else 0.0,
    })

# ── DUPLICATES ─────────────────────────────────────────────────────────────────
policyholders_raw.extend(random.sample(policyholders_raw, 60))
claims_raw.extend(random.sample(claims_raw, 50))

# ── SAVE ───────────────────────────────────────────────────────────────────────
pd.DataFrame(policyholders_raw).to_csv("Data/raw/policyholders_raw.csv", index=False)
pd.DataFrame(vehicles_raw).to_csv("Data/raw/vehicles_raw.csv", index=False)
pd.DataFrame(policies_raw).to_csv("Data/raw/policies_raw.csv", index=False)
pd.DataFrame(claims_raw).to_csv("Data/raw/claims_raw.csv", index=False)
pd.DataFrame(payments_raw).to_csv("Data/raw/payments_raw.csv", index=False)

print("=" * 55)
print("  Car Insurance Dataset Generated Successfully!")
print("=" * 55)
print(f"  policyholders_raw.csv → {len(policyholders_raw)} rows")
print(f"  vehicles_raw.csv      → {len(vehicles_raw)} rows")
print(f"  policies_raw.csv      → {len(policies_raw)} rows")
print(f"  claims_raw.csv        → {len(claims_raw)} rows")
print(f"  payments_raw.csv      → {len(payments_raw)} rows")
print()
print("Mess introduced:")
print("  ✗ Missing values       → name, DOB, phone, credit score, mileage")
print("  ✗ Mixed date formats   → YYYY-MM-DD / DD/MM/YYYY / MM-DD-YYYY")
print("  ✗ Currency strings     → '$1,200.00' instead of 1200.0")
print("  ✗ Boolean chaos        → Yes/No/Y/N/1/0/TRUE/FALSE mixed")
print("  ✗ Inconsistent casing  → Male/MALE/male/M/m mixed")
print("  ✗ Negative values      → claim amounts, license years")
print("  ✗ Illogical data       → end date before start date")
print("  ✗ Out of range         → mileage > 500k, settled > claimed")
print("  ✗ Duplicate rows       → 60 policyholders, 50 claims")
print("  ✗ Fraud signals        → flagged in is_fraud_flag column")
