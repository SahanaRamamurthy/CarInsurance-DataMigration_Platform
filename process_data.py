import pandas as pd
import numpy as np
import os
import re

RAW = "Data/raw"
PROCESSED = "Data/processed"
os.makedirs(PROCESSED, exist_ok=True)


def parse_date(series):
    """Try multiple date formats and return a uniform YYYY-MM-DD string."""
    formats = ["%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y", "%Y-%m-%d",
               "%d %b %Y", "%d %B %Y", "%m/%d/%Y"]
    out = pd.Series([pd.NaT] * len(series), index=series.index)
    remaining = series.copy()
    for fmt in formats:
        mask = out.isna() & remaining.notna()
        if not mask.any():
            break
        parsed = pd.to_datetime(remaining[mask], format=fmt, errors="coerce")
        out[mask] = parsed
    return pd.to_datetime(out, errors="coerce")


# ── POLICYHOLDERS ─────────────────────────────────────────────────────────────
def clean_policyholders():
    df = pd.read_csv(f"{RAW}/policyholders_raw.csv")

    # Standardise gender
    gender_map = {"M": "Male", "F": "Female", "male": "Male", "female": "Female",
                  "m": "Male", "f": "Female", "MALE": "Male", "FEMALE": "Female"}
    df["gender"] = df["gender"].map(gender_map).fillna("Unknown")

    # Standardise marital status
    marital_map = {"S": "Single", "M": "Married", "D": "Divorced", "W": "Widowed",
                   "single": "Single", "married": "Married"}
    df["marital_status"] = df["marital_status"].map(marital_map).fillna("Unknown")

    # Clean phone — keep digits only, store as string
    df["phone"] = df["phone"].astype(str).str.replace(r"\D", "", regex=True).str[-10:]
    df["phone"] = df["phone"].where(df["phone"].str.len() == 10, other=None)

    # Email lowercase
    df["email"] = df["email"].str.lower().str.strip()

    # DOB
    df["date_of_birth"] = parse_date(df["date_of_birth"]).dt.strftime("%Y-%m-%d")

    # Drop rows missing critical fields
    df = df.dropna(subset=["policyholder_id", "full_name"])
    df = df.drop_duplicates(subset=["policyholder_id"])

    # Fill numeric nulls
    df["credit_score"] = df["credit_score"].fillna(df["credit_score"].median()).round(0).astype(int)
    df["prior_claims_count"] = df["prior_claims_count"].fillna(0).astype(int)
    df["license_years"] = df["license_years"].fillna(0).astype(int)
    df["age"] = df["age"].fillna(0).astype(int)

    df.to_csv(f"{PROCESSED}/policyholders.csv", index=False)
    print(f"  policyholders: {len(df)} rows")


# ── VEHICLES ──────────────────────────────────────────────────────────────────
def clean_vehicles():
    df = pd.read_csv(f"{RAW}/vehicles_raw.csv")

    # Remove $ and commas from vehicle_value
    df["vehicle_value_usd"] = (df["vehicle_value_usd"].astype(str)
                               .str.replace(r"[\$,]", "", regex=True)
                               .pipe(pd.to_numeric, errors="coerce"))
    df["vehicle_value_usd"] = df["vehicle_value_usd"].fillna(df["vehicle_value_usd"].median()).round(2)

    # Standardise fuel_type capitalisation
    df["fuel_type"] = df["fuel_type"].str.capitalize().str.strip()

    # Standardise is_modified to boolean
    bool_map = {"Y": True, "N": False, "Yes": True, "No": False,
                "TRUE": True, "FALSE": False, "1": True, "0": False,
                True: True, False: False}
    df["is_modified"] = df["is_modified"].astype(str).map(bool_map).fillna(False)

    df["mileage"] = df["mileage"].fillna(0).astype(int)

    df = df.dropna(subset=["vehicle_id", "policyholder_id"])
    df = df.drop_duplicates(subset=["vehicle_id"])

    df.to_csv(f"{PROCESSED}/vehicles.csv", index=False)
    print(f"  vehicles:      {len(df)} rows")


# ── POLICIES ──────────────────────────────────────────────────────────────────
def clean_policies():
    df = pd.read_csv(f"{RAW}/policies_raw.csv")

    df["start_date"] = parse_date(df["start_date"]).dt.strftime("%Y-%m-%d")
    df["end_date"] = parse_date(df["end_date"]).dt.strftime("%Y-%m-%d")

    # Standardise is_active
    active_map = {"Y": True, "N": False, "Yes": True, "No": False,
                  "TRUE": True, "FALSE": False, True: True, False: False}
    df["is_active"] = df["is_active"].astype(str).map(active_map).fillna(False)

    # Standardise coverage_type capitalisation
    df["coverage_type"] = df["coverage_type"].str.title().str.strip()

    df["premium_usd"] = pd.to_numeric(df["premium_usd"], errors="coerce").fillna(0).round(2)
    df["deductible_usd"] = pd.to_numeric(df["deductible_usd"], errors="coerce").fillna(0).round(2)
    df["coverage_amount_usd"] = pd.to_numeric(df["coverage_amount_usd"], errors="coerce").fillna(0).round(2)

    df = df.dropna(subset=["policy_id", "policyholder_id", "vehicle_id"])
    df = df.drop_duplicates(subset=["policy_id"])

    df.to_csv(f"{PROCESSED}/policies.csv", index=False)
    print(f"  policies:      {len(df)} rows")


# ── CLAIMS ────────────────────────────────────────────────────────────────────
def clean_claims():
    df = pd.read_csv(f"{RAW}/claims_raw.csv")

    df["claim_date"] = parse_date(df["claim_date"]).dt.strftime("%Y-%m-%d")

    # Standardise status capitalisation
    df["status"] = df["status"].str.strip().str.title()

    # is_fraud_flag
    fraud_map = {"Yes": True, "No": False, "Y": True, "N": False,
                 "TRUE": True, "FALSE": False, True: True, False: False}
    df["is_fraud_flag"] = df["is_fraud_flag"].astype(str).map(fraud_map).fillna(False)

    df["claim_amount_usd"] = pd.to_numeric(df["claim_amount_usd"], errors="coerce").fillna(0).round(2)
    df["settled_amount_usd"] = pd.to_numeric(df["settled_amount_usd"], errors="coerce").fillna(0).round(2)
    df["days_to_report"] = pd.to_numeric(df["days_to_report"], errors="coerce").fillna(0).astype(int)

    df = df.dropna(subset=["claim_id", "policy_id"])
    df = df.drop_duplicates(subset=["claim_id"])

    df.to_csv(f"{PROCESSED}/claims.csv", index=False)
    print(f"  claims:        {len(df)} rows")


# ── PAYMENTS ──────────────────────────────────────────────────────────────────
def clean_payments():
    df = pd.read_csv(f"{RAW}/payments_raw.csv")

    df["payment_date"] = parse_date(df["payment_date"]).dt.strftime("%Y-%m-%d")

    df["status"] = df["status"].str.strip().str.upper()

    late_map = {"1": True, "0": False, "True": True, "False": False,
                "Yes": True, "No": False, True: True, False: False}
    df["is_late"] = df["is_late"].astype(str).map(late_map).fillna(False)

    df["amount_usd"] = pd.to_numeric(df["amount_usd"], errors="coerce").fillna(0).round(2)
    df["late_fee_usd"] = pd.to_numeric(df["late_fee_usd"], errors="coerce").fillna(0).round(2)

    df["payment_method"] = df["payment_method"].str.strip().str.title()

    df = df.dropna(subset=["payment_id", "policy_id"])
    df = df.drop_duplicates(subset=["payment_id"])

    df.to_csv(f"{PROCESSED}/payments.csv", index=False)
    print(f"  payments:      {len(df)} rows")


if __name__ == "__main__":
    print("Cleaning raw data...")
    clean_policyholders()
    clean_vehicles()
    clean_policies()
    clean_claims()
    clean_payments()
    print("Done — processed files saved to Data/processed/")
