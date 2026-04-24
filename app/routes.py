from flask import jsonify, send_file
from sqlalchemy import text
from .db import engine
import os


def register_routes(app):

    # ── DASHBOARD ─────────────────────────────────────────────────────────────
    @app.route("/dashboard")
    def dashboard():
        return send_file(os.path.join(os.path.dirname(__file__), '..', 'dashboard.html'))

    # ── 1. HOME ───────────────────────────────────────────────────────────────
    @app.route("/")
    def home():
        return jsonify({
            "project": "CarInsure DataMigration Platform",
            "status": "running",
            "endpoints": [
                "/summary",
                "/migration/health",
                "/policyholders/high-risk",
                "/policyholders/high-risk/count",
                "/claims/fraud",
                "/claims/summary",
                "/policies/expiring-soon",
                "/payments/late",
                "/vehicles/<vehicle_id>"
            ]
        })

    # ── 2. SUMMARY — row counts for all 5 tables ──────────────────────────────
    @app.route("/summary")
    def get_summary():
        query = text("""
            SELECT 'policyholders'  AS table_name, COUNT(*) AS row_count FROM policyholders
            UNION ALL
            SELECT 'vehicles',  COUNT(*) FROM vehicles
            UNION ALL
            SELECT 'policies',  COUNT(*) FROM policies
            UNION ALL
            SELECT 'claims',    COUNT(*) FROM claims
            UNION ALL
            SELECT 'payments',  COUNT(*) FROM payments
            ORDER BY table_name;
        """)
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = [{"table_name": r[0], "row_count": r[1]} for r in result]
        return jsonify(rows)

    # ── 3. HIGH-RISK POLICYHOLDERS (credit score < 550 OR prior claims >= 5) ──
    @app.route("/policyholders/high-risk")
    def get_high_risk_policyholders():
        query = text("""
            SELECT policyholder_id, full_name, state, credit_score,
                   prior_claims_count, age, gender
            FROM policyholders
            WHERE credit_score < 550 OR prior_claims_count >= 5
            ORDER BY prior_claims_count DESC, credit_score ASC;
        """)
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = [
                {
                    "policyholder_id":   r[0],
                    "full_name":         r[1],
                    "state":             r[2],
                    "credit_score":      r[3],
                    "prior_claims_count": r[4],
                    "age":               r[5],
                    "gender":            r[6]
                }
                for r in result
            ]
        return jsonify(rows)

    # ── 4. HIGH-RISK COUNT ────────────────────────────────────────────────────
    @app.route("/policyholders/high-risk/count")
    def get_high_risk_count():
        query = text("""
            SELECT COUNT(*) FROM policyholders
            WHERE credit_score < 550 OR prior_claims_count >= 5;
        """)
        with engine.connect() as conn:
            count = conn.execute(query).scalar()
        return jsonify({"high_risk_policyholders": count})

    # ── 5. FRAUD-FLAGGED CLAIMS ───────────────────────────────────────────────
    @app.route("/claims/fraud")
    def get_fraud_claims():
        query = text("""
            SELECT c.claim_id, c.policy_id, c.claim_date, c.claim_type,
                   c.claim_amount_usd, c.status, c.days_to_report,
                   p.policyholder_id
            FROM claims c
            JOIN policies p ON c.policy_id = p.policy_id
            WHERE c.is_fraud_flag = TRUE
            ORDER BY c.claim_amount_usd DESC;
        """)
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = [
                {
                    "claim_id":          r[0],
                    "policy_id":         r[1],
                    "claim_date":        str(r[2]),
                    "claim_type":        r[3],
                    "claim_amount_usd":  float(r[4]),
                    "status":            r[5],
                    "days_to_report":    r[6],
                    "policyholder_id":   r[7]
                }
                for r in result
            ]
        return jsonify(rows)

    # ── 6. CLAIMS SUMMARY — avg, total, fraud rate by claim type ──────────────
    @app.route("/claims/summary")
    def get_claims_summary():
        query = text("""
            SELECT
                claim_type,
                COUNT(*)                                        AS total_claims,
                ROUND(AVG(claim_amount_usd)::numeric, 2)        AS avg_claim_amount,
                SUM(claim_amount_usd)                           AS total_claimed,
                SUM(settled_amount_usd)                         AS total_settled,
                SUM(CASE WHEN is_fraud_flag THEN 1 ELSE 0 END)  AS fraud_count
            FROM claims
            GROUP BY claim_type
            ORDER BY total_claims DESC;
        """)
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = [
                {
                    "claim_type":        r[0],
                    "total_claims":      r[1],
                    "avg_claim_amount":  float(r[2]),
                    "total_claimed":     float(r[3]),
                    "total_settled":     float(r[4]),
                    "fraud_count":       r[5]
                }
                for r in result
            ]
        return jsonify(rows)

    # ── 7. POLICIES EXPIRING IN NEXT 30 DAYS ─────────────────────────────────
    @app.route("/policies/expiring-soon")
    def get_expiring_policies():
        query = text("""
            SELECT po.policy_id, po.coverage_type, po.end_date,
                   po.premium_usd, po.is_active,
                   ph.full_name, ph.email, ph.phone
            FROM policies po
            JOIN policyholders ph ON po.policyholder_id = ph.policyholder_id
            WHERE po.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
              AND po.is_active = TRUE
            ORDER BY po.end_date ASC;
        """)
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = [
                {
                    "policy_id":     r[0],
                    "coverage_type": r[1],
                    "end_date":      str(r[2]),
                    "premium_usd":   float(r[3]),
                    "is_active":     r[4],
                    "full_name":     r[5],
                    "email":         r[6],
                    "phone":         r[7]
                }
                for r in result
            ]
        return jsonify(rows)

    # ── 8. LATE PAYMENTS ──────────────────────────────────────────────────────
    @app.route("/payments/late")
    def get_late_payments():
        query = text("""
            SELECT py.payment_id, py.policy_id, py.payment_date,
                   py.amount_usd, py.late_fee_usd, py.payment_method,
                   ph.full_name, ph.state
            FROM payments py
            JOIN policies po  ON py.policy_id = po.policy_id
            JOIN policyholders ph ON po.policyholder_id = ph.policyholder_id
            WHERE py.is_late = TRUE
            ORDER BY py.late_fee_usd DESC;
        """)
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = [
                {
                    "payment_id":     r[0],
                    "policy_id":      r[1],
                    "payment_date":   str(r[2]),
                    "amount_usd":     float(r[3]),
                    "late_fee_usd":   float(r[4]),
                    "payment_method": r[5],
                    "full_name":      r[6],
                    "state":          r[7]
                }
                for r in result
            ]
        return jsonify(rows)

    # ── 9. VEHICLE DETAILS by ID ──────────────────────────────────────────────
    @app.route("/vehicles/<vehicle_id>")
    def get_vehicle(vehicle_id):
        query = text("""
            SELECT v.vehicle_id, v.make, v.model, v.year, v.color,
                   v.vehicle_value_usd, v.mileage, v.fuel_type, v.vin, v.is_modified,
                   ph.full_name, ph.state
            FROM vehicles v
            JOIN policyholders ph ON v.policyholder_id = ph.policyholder_id
            WHERE v.vehicle_id = :vid;
        """)
        with engine.connect() as conn:
            row = conn.execute(query, {"vid": vehicle_id.upper()}).fetchone()
        if not row:
            return jsonify({"error": f"Vehicle {vehicle_id} not found"}), 404
        return jsonify({
            "vehicle_id":        row[0],
            "make":              row[1],
            "model":             row[2],
            "year":              row[3],
            "color":             row[4],
            "vehicle_value_usd": float(row[5]),
            "mileage":           row[6],
            "fuel_type":         row[7],
            "vin":               row[8],
            "is_modified":       row[9],
            "owner":             row[10],
            "state":             row[11]
        })

    # ── 10. MIGRATION HEALTH CHECK ────────────────────────────────────────────
    @app.route("/migration/health")
    def get_migration_health():
        query = text("""
            SELECT
                (SELECT COUNT(*) FROM policyholders)                                AS total_policyholders,
                (SELECT COUNT(*) FROM vehicles)                                     AS total_vehicles,
                (SELECT COUNT(*) FROM policies)                                     AS total_policies,
                (SELECT COUNT(*) FROM claims)                                       AS total_claims,
                (SELECT COUNT(*) FROM payments)                                     AS total_payments,
                (SELECT COUNT(*) FROM policyholders
                 WHERE credit_score < 550 OR prior_claims_count >= 5)               AS high_risk_count,
                (SELECT COUNT(*) FROM claims WHERE is_fraud_flag = TRUE)            AS fraud_claims_count,
                (SELECT COUNT(*) FROM payments WHERE is_late = TRUE)                AS late_payments_count,
                (SELECT ROUND(AVG(premium_usd)::numeric, 2) FROM policies)          AS avg_premium_usd,
                (SELECT ROUND(AVG(credit_score)::numeric, 1) FROM policyholders)    AS avg_credit_score;
        """)
        with engine.connect() as conn:
            row = conn.execute(query).fetchone()
        return jsonify({
            "total_policyholders":  row[0],
            "total_vehicles":       row[1],
            "total_policies":       row[2],
            "total_claims":         row[3],
            "total_payments":       row[4],
            "high_risk_count":      row[5],
            "fraud_claims_count":   row[6],
            "late_payments_count":  row[7],
            "avg_premium_usd":      float(row[8]),
            "avg_credit_score":     float(row[9])
        })
