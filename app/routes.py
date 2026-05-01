from flask import jsonify, send_file, request, session, redirect, url_for, render_template_string, send_from_directory
from sqlalchemy import text
from .db import engine
from .auth import verify_user
from functools import wraps
import os


# ── AUTH HELPERS ──────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def super_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        if session["user"]["role"] != "super_admin":
            return render_template_string("""
                <div style="font-family:sans-serif;text-align:center;padding:80px;background:#0f1117;color:#fc8181;min-height:100vh">
                    <h2>Access Denied</h2>
                    <p style="color:#718096">You don't have permission to view this page.</p>
                    <a href="/dashboard" style="color:#667eea">Back to Dashboard</a>
                </div>"""), 403
        return f(*args, **kwargs)
    return decorated


def register_routes(app):

    # ── STATIC ASSETS ─────────────────────────────────────────────────────────
    @app.route("/assets/<path:filename>")
    def assets(filename):
        return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'assets'), filename)

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = ""
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            user = verify_user(username, password)
            if user:
                session["user"] = user
                return redirect("/dashboard")
            else:
                error = "Invalid username or password"

        return send_file(os.path.join(os.path.dirname(__file__), '..', 'login.html'))

    @app.route("/login-error")
    def login_error():
        return send_file(os.path.join(os.path.dirname(__file__), '..', 'login.html'))

    # ── LOGOUT ────────────────────────────────────────────────────────────────
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

    # ── CURRENT USER API ──────────────────────────────────────────────────────
    @app.route("/auth/me")
    def auth_me():
        if "user" not in session:
            return jsonify({"logged_in": False}), 401
        return jsonify({"logged_in": True, **session["user"]})

    # ── LOGIN POST (AJAX) ─────────────────────────────────────────────────────
    @app.route("/auth/login", methods=["POST"])
    def auth_login():
        data = request.get_json()
        user = verify_user(data.get("username", ""), data.get("password", ""))
        if user:
            session["user"] = user
            return jsonify({"success": True, "role": user["role"], "display_name": user["display_name"]})
        return jsonify({"success": False, "error": "Invalid username or password"}), 401

    # ── DASHBOARD ─────────────────────────────────────────────────────────────
    @app.route("/dashboard")
    @login_required
    def dashboard():
        return send_file(os.path.join(os.path.dirname(__file__), '..', 'dashboard.html'))

    # ── SUPER ADMIN PANEL ─────────────────────────────────────────────────────
    @app.route("/admin")
    @super_admin_required
    def admin_panel():
        return send_file(os.path.join(os.path.dirname(__file__), '..', 'admin.html'))

    # ── HOME ──────────────────────────────────────────────────────────────────
    @app.route("/")
    def home():
        if "user" not in session:
            return redirect("/login")
        return redirect("/dashboard")

    # ── 2. SUMMARY ────────────────────────────────────────────────────────────
    @app.route("/summary")
    @login_required
    def get_summary():
        query = text("""
            SELECT 'policyholders' AS table_name, COUNT(*) AS row_count FROM policyholders
            UNION ALL SELECT 'vehicles',  COUNT(*) FROM vehicles
            UNION ALL SELECT 'policies',  COUNT(*) FROM policies
            UNION ALL SELECT 'claims',    COUNT(*) FROM claims
            UNION ALL SELECT 'payments',  COUNT(*) FROM payments
            ORDER BY table_name;
        """)
        with engine.connect() as conn:
            rows = [{"table_name": r[0], "row_count": r[1]} for r in conn.execute(query)]
        return jsonify(rows)

    # ── 3. HIGH-RISK POLICYHOLDERS ────────────────────────────────────────────
    @app.route("/policyholders/high-risk")
    @login_required
    def get_high_risk_policyholders():
        query = text("""
            SELECT policyholder_id, full_name, state, credit_score,
                   prior_claims_count, age, gender
            FROM policyholders
            WHERE credit_score < 550 OR prior_claims_count >= 5
            ORDER BY prior_claims_count DESC, credit_score ASC;
        """)
        with engine.connect() as conn:
            rows = [{"policyholder_id": r[0], "full_name": r[1], "state": r[2],
                     "credit_score": r[3], "prior_claims_count": r[4], "age": r[5], "gender": r[6]}
                    for r in conn.execute(query)]
        return jsonify(rows)

    # ── 4. HIGH-RISK COUNT ────────────────────────────────────────────────────
    @app.route("/policyholders/high-risk/count")
    @login_required
    def get_high_risk_count():
        with engine.connect() as conn:
            count = conn.execute(text(
                "SELECT COUNT(*) FROM policyholders WHERE credit_score < 550 OR prior_claims_count >= 5"
            )).scalar()
        return jsonify({"high_risk_policyholders": count})

    # ── 5. FRAUD CLAIMS ───────────────────────────────────────────────────────
    @app.route("/claims/fraud")
    @login_required
    def get_fraud_claims():
        query = text("""
            SELECT c.claim_id, c.policy_id, c.claim_date, c.claim_type,
                   c.claim_amount_usd, c.status, c.days_to_report, p.policyholder_id
            FROM claims c JOIN policies p ON c.policy_id = p.policy_id
            WHERE c.is_fraud_flag = TRUE ORDER BY c.claim_amount_usd DESC;
        """)
        with engine.connect() as conn:
            rows = [{"claim_id": r[0], "policy_id": r[1], "claim_date": str(r[2]),
                     "claim_type": r[3], "claim_amount_usd": float(r[4]),
                     "status": r[5], "days_to_report": r[6], "policyholder_id": r[7]}
                    for r in conn.execute(query)]
        return jsonify(rows)

    # ── 6. CLAIMS SUMMARY ─────────────────────────────────────────────────────
    @app.route("/claims/summary")
    @login_required
    def get_claims_summary():
        query = text("""
            SELECT claim_type, COUNT(*) AS total_claims,
                   ROUND(AVG(claim_amount_usd)::numeric, 2) AS avg_claim_amount,
                   SUM(claim_amount_usd) AS total_claimed,
                   SUM(settled_amount_usd) AS total_settled,
                   SUM(CASE WHEN is_fraud_flag THEN 1 ELSE 0 END) AS fraud_count
            FROM claims GROUP BY claim_type ORDER BY total_claims DESC;
        """)
        with engine.connect() as conn:
            rows = [{"claim_type": r[0], "total_claims": r[1], "avg_claim_amount": float(r[2]),
                     "total_claimed": float(r[3]), "total_settled": float(r[4]), "fraud_count": r[5]}
                    for r in conn.execute(query)]
        return jsonify(rows)

    # ── 7. EXPIRING POLICIES ──────────────────────────────────────────────────
    @app.route("/policies/expiring-soon")
    @login_required
    def get_expiring_policies():
        query = text("""
            SELECT po.policy_id, po.coverage_type, po.end_date, po.premium_usd,
                   po.is_active, ph.full_name, ph.email, ph.phone
            FROM policies po JOIN policyholders ph ON po.policyholder_id = ph.policyholder_id
            WHERE po.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
              AND po.is_active = TRUE ORDER BY po.end_date ASC;
        """)
        with engine.connect() as conn:
            rows = [{"policy_id": r[0], "coverage_type": r[1], "end_date": str(r[2]),
                     "premium_usd": float(r[3]), "is_active": r[4],
                     "full_name": r[5], "email": r[6], "phone": r[7]}
                    for r in conn.execute(query)]
        return jsonify(rows)

    # ── 8. LATE PAYMENTS ──────────────────────────────────────────────────────
    @app.route("/payments/late")
    @login_required
    def get_late_payments():
        query = text("""
            SELECT py.payment_id, py.policy_id, py.payment_date, py.amount_usd,
                   py.late_fee_usd, py.payment_method, ph.full_name, ph.state
            FROM payments py
            JOIN policies po ON py.policy_id = po.policy_id
            JOIN policyholders ph ON po.policyholder_id = ph.policyholder_id
            WHERE py.is_late = TRUE ORDER BY py.late_fee_usd DESC;
        """)
        with engine.connect() as conn:
            rows = [{"payment_id": r[0], "policy_id": r[1], "payment_date": str(r[2]),
                     "amount_usd": float(r[3]), "late_fee_usd": float(r[4]),
                     "payment_method": r[5], "full_name": r[6], "state": r[7]}
                    for r in conn.execute(query)]
        return jsonify(rows)

    # ── 9. VEHICLE DETAILS ────────────────────────────────────────────────────
    @app.route("/vehicles/<vehicle_id>")
    @login_required
    def get_vehicle(vehicle_id):
        query = text("""
            SELECT v.vehicle_id, v.make, v.model, v.year, v.color,
                   v.vehicle_value_usd, v.mileage, v.fuel_type, v.vin, v.is_modified,
                   ph.full_name, ph.state
            FROM vehicles v JOIN policyholders ph ON v.policyholder_id = ph.policyholder_id
            WHERE v.vehicle_id = :vid;
        """)
        with engine.connect() as conn:
            row = conn.execute(query, {"vid": vehicle_id.upper()}).fetchone()
        if not row:
            return jsonify({"error": f"Vehicle {vehicle_id} not found"}), 404
        return jsonify({"vehicle_id": row[0], "make": row[1], "model": row[2], "year": row[3],
                        "color": row[4], "vehicle_value_usd": float(row[5]), "mileage": row[6],
                        "fuel_type": row[7], "vin": row[8], "is_modified": row[9],
                        "owner": row[10], "state": row[11]})

    # ── 10. MIGRATION HEALTH ──────────────────────────────────────────────────
    @app.route("/migration/health")
    @login_required
    def get_migration_health():
        query = text("""
            SELECT
                (SELECT COUNT(*) FROM policyholders) AS total_policyholders,
                (SELECT COUNT(*) FROM vehicles)      AS total_vehicles,
                (SELECT COUNT(*) FROM policies)      AS total_policies,
                (SELECT COUNT(*) FROM claims)        AS total_claims,
                (SELECT COUNT(*) FROM payments)      AS total_payments,
                (SELECT COUNT(*) FROM policyholders WHERE credit_score < 550 OR prior_claims_count >= 5) AS high_risk_count,
                (SELECT COUNT(*) FROM claims WHERE is_fraud_flag = TRUE)         AS fraud_claims_count,
                (SELECT COUNT(*) FROM payments WHERE is_late = TRUE)             AS late_payments_count,
                (SELECT ROUND(AVG(premium_usd)::numeric, 2) FROM policies)       AS avg_premium_usd,
                (SELECT ROUND(AVG(credit_score)::numeric, 1) FROM policyholders) AS avg_credit_score;
        """)
        with engine.connect() as conn:
            row = conn.execute(query).fetchone()
        return jsonify({
            "total_policyholders": row[0], "total_vehicles": row[1],
            "total_policies": row[2],      "total_claims": row[3],
            "total_payments": row[4],      "high_risk_count": row[5],
            "fraud_claims_count": row[6],  "late_payments_count": row[7],
            "avg_premium_usd": float(row[8]), "avg_credit_score": float(row[9])
        })

    # ── 11. ADMIN — user list (super admin only) ──────────────────────────────
    @app.route("/admin/users")
    @super_admin_required
    def admin_users():
        from .auth import USERS
        users = [{"username": u, "role": d["role"], "display_name": d["display_name"]}
                 for u, d in USERS.items()]
        return jsonify(users)
