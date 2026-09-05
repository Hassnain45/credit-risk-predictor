import os
import sys
import subprocess
import time
import pandas as pd
import requests
import streamlit as st

API_URL = http://127.0.0.1:8000

def start_backend_daemon():
    try:
        requests.get(f{API_URL}/health, timeout=1)
    except Exception:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env = os.environ.copy()
        env["PYTHONPATH"] = root_dir

        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
            cwd=root_dir,
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        for _ in range(15):
            try:
                if requests.get(f"{API_URL}/health", timeout=1).status_code == 200:
                    break
            except Exception:
                time.sleep(1)

start_backend_daemon()

st.set_page_config(
    page_title="RiskFlow | Institutional Credit Underwriting Desk",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Institutional Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .badge-approved {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-rejected {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .risk-driver-box {
        background: rgba(239, 68, 68, 0.06);
        border-left: 3px solid #EF4444;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .action-box {
        background: rgba(59, 130, 246, 0.06);
        border-left: 3px solid #3B82F6;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

if "user_submissions" not in st.session_state:
    st.session_state["user_submissions"] = []

if "preset_data" not in st.session_state:
    st.session_state["preset_data"] = {
        "name": "Sarah Connor",
        "duration": 12,
        "amount": 1800,
        "rate": 2,
        "age": 42,
        "checking": ">=200",
        "history": "all paid",
        "savings": ">=1000",
        "employment": ">=7",
        "housing": "own",
        "purpose": "new car",
        "residence": 4
    }

def set_prime_borrower():
    st.session_state["preset_data"] = {
        "name": "Sarah Connor",
        "duration": 12,
        "amount": 1800,
        "rate": 2,
        "age": 42,
        "checking": ">=200",
        "history": "all paid",
        "savings": ">=1000",
        "employment": ">=7",
        "housing": "own",
        "purpose": "new car",
        "residence": 4
    }

def set_subprime_borrower():
    st.session_state["preset_data"] = {
        "name": "Alex Morgan",
        "duration": 36,
        "amount": 6500,
        "rate": 4,
        "age": 24,
        "checking": "<0",
        "history": "delayed previously",
        "savings": "<100",
        "employment": "<1",
        "housing": "rent",
        "purpose": "business",
        "residence": 1
    }

def mask_name(name: str) -> str:
    parts = name.split()
    masked = [p[0] + "*" * (len(p) - 1) if len(p) > 1 else p for p in parts]
    return " ".join(masked)

with st.sidebar:
    st.title("⚖️ RiskFlow Engine")
    st.caption("Institutional Credit Decisioning Architecture")
    
    try:
        health = requests.get(f"{API_URL}/health", timeout=2).json()
        st.success(f"Backend Active\nModel: {health['model_version']}")
        st.metric("Policy Tolerance (τ*)", f"{health['threshold']*100:.1f}%", help="Cost-minimized decision cutoff")
    except Exception:
        st.error("Connecting to scoring microservice...")

    st.divider()
    st.subheader("⚡ Interactive Profiles")
    st.caption("Load verified profiles to evaluate cutoff mechanics:")
    col_pre1, col_pre2 = st.columns(2)
    with col_pre1:
        st.button("🟢 Prime", on_click=set_prime_borrower, width="stretch", help="Low-risk profile")
    with col_pre2:
        st.button("🔴 Subprime", on_click=set_subprime_borrower, width="stretch", help="Distressed profile")

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("Credit Risk Underwriting Portal")
    st.markdown("Cost-Calibrated Gradient Boosting • SHAP FCRA Reason Codes • Automated Recourse")
with header_col2:
    st.caption("Regulatory Compliance:\nUS FCRA § 615(a) / EU AI Act Article 14")

tab_underwrite, tab_audit = st.tabs(["📝 Underwriting Workbench", "🔒 Compliance Audit Trail"])

preset = st.session_state["preset_data"]

with tab_underwrite:
    with st.form("loan_application_form"):
        st.subheader("1. Facility & Loan Parameters")
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            applicant_name = st.text_input("Applicant Full Name", value=preset["name"])
        with f_col2:
            credit_amount = st.number_input("Requested Facility (DM)", min_value=250, max_value=20000, value=preset["amount"], step=250)
        with f_col3:
            duration_months = st.slider("Facility Term (Months)", min_value=4, max_value=72, value=preset["duration"])

        st.subheader("2. Financial Standing & History")
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            checking_opts = [">=200", "0<=X<200", "<0", "no checking"]
            checking_status = st.selectbox("Checking Liquidity", checking_opts, index=checking_opts.index(preset["checking"]))
        with b_col2:
            savings_opts = [">=1000", "500<=X<1000", "100<=X<500", "<100", "no known savings"]
            savings_status = st.selectbox("Savings Reserves", savings_opts, index=savings_opts.index(preset["savings"]))
        with b_col3:
            history_opts = ["all paid", "existing paid", "critical/other existing credit", "delayed previously", "no credits/all paid"]
            credit_history = st.selectbox("Historical Repayment Pattern", history_opts, index=history_opts.index(preset["history"]))

        st.subheader("3. Borrower Demographic & Stability Indicators")
        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        with d_col1:
            age = st.slider("Borrower Age", 18, 75, preset["age"])
        with d_col2:
            emp_opts = [">=7", "4<=X<7", "1<=X<4", "<1", "unemployed"]
            employment = st.selectbox("Tenure at Current Employer", emp_opts, index=emp_opts.index(preset["employment"]))
        with d_col3:
            housing_opts = ["own", "rent", "for free"]
            housing = st.selectbox("Residential Tenure", housing_opts, index=housing_opts.index(preset["housing"]))
        with d_col4:
            purpose_opts = ["new car", "used car", "business", "education", "repairs", "radio/tv", "furniture/equipment"]
            purpose = st.selectbox("Credit Purpose", purpose_opts, index=purpose_opts.index(preset["purpose"]))

        installment_rate = st.slider("Debt Service Ratio (% of Disposable Income)", 1, 4, preset["rate"])
        residence_since = preset["residence"]

        submit_btn = st.form_submit_button("⚡ Run Decisioning Engine", width="stretch")

    if submit_btn:
        payload = {
            "applicant_name": applicant_name,
            "duration_months": int(duration_months),
            "credit_amount": float(credit_amount),
            "installment_rate": int(installment_rate),
            "age": int(age),
            "residence_since": int(residence_since),
            "existing_credits": 1,
            "num_dependents": 1,
            "checking_status": checking_status,
            "credit_history": credit_history,
            "savings_status": savings_status,
            "employment": employment,
            "housing": housing,
            "purpose": purpose
        }

        with st.spinner("Executing inference and calculating SHAP marginals..."):
            try:
                resp = requests.post(f"{API_URL}/api/v1/underwrite", json=payload)
                if resp.status_code == 200:
                    res = resp.json()
                    pd_score = res["probability_of_default"]
                    threshold = res["threshold_applied"]
                    is_approved = res["decision"] == "APPROVED"

                    st.session_state["user_submissions"].insert(0, {
                        "id": res["application_id"],
                        "applicant_name": res["applicant_name"],
                        "credit_amount": credit_amount,
                        "duration_months": duration_months,
                        "default_probability": pd_score,
                        "decision": res["decision"],
                        "created_at": pd.Timestamp.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    })

                    st.divider()
                    
                    dec_col1, dec_col2, dec_col3 = st.columns([1.2, 1.2, 2])

                    with dec_col1:
                        st.markdown("**Underwriting Verdict**")
                        if is_approved:
                            st.markdown('<span class="status-badge badge-approved">VERDICT: APPROVED</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="status-badge badge-rejected">VERDICT: DECLINED</span>', unsafe_allow_html=True)
                        st.caption(f"Audit Identifier: #{res['application_id']}")

                    with dec_col2:
                        st.metric(
                            label="Default Probability (PD)",
                            value=f"{pd_score * 100:.1f}%",
                            delta=f"{(pd_score - threshold)*100:+.1f}% vs Cutoff",
                            delta_color="inverse"
                        )

                    with dec_col3:
                        st.markdown("**Risk vs. Policy Boundary**")
                        st.progress(min(max(pd_score, 0.0), 1.0))
                        st.caption(f"Institutional Limit: {threshold*100:.1f}% | Evaluated via {res['model_version']}")

                    st.divider()

                    exp_col1, exp_col2 = st.columns(2)

                    with exp_col1:
                        st.subheader("Adverse Action Attribution (FCRA § 615)")
                        if not is_approved:
                            st.caption("Top risk drivers isolated via local SHAP attribution:")
                            for reason in res["adverse_action_reasons"]:
                                st.markdown(f'<div class="risk-driver-box">⚠️ {reason}</div>', unsafe_allow_html=True)
                        else:
                            st.success("Risk indicators clear institutional safety criteria. No adverse codes generated.")

                    with exp_col2:
                        st.subheader("Counterfactual Path to Recourse")
                        if not is_approved:
                            st.caption("Simulated adjustments required to achieve policy compliance:")
                            for cf in res["counterfactual_recommendations"]:
                                st.markdown(f'<div class="action-box">💡 {cf}</div>', unsafe_allow_html=True)
                        else:
                            st.info("Applicant qualifies under prime credit guidelines.")
                            st.balloons()
                else:
                    st.error(f"Scoring Engine Error ({resp.status_code}): {resp.text}")
            except Exception as e:
                st.error(f"Failed to communicate with scoring service: {e}")

with tab_audit:
    st.subheader("Regulatory Audit Trail & Access Governance")
    
    view_mode = st.radio(
        "Select Clearance Level:",
        ["👤 Active Session Records (Local)", "🔑 Institutional Compliance Ledger (Restricted)"],
        horizontal=True
    )

    if view_mode == "👤 Active Session Records (Local)":
        st.caption("Confined strictly to evaluations executed during your current browser instance.")
        if st.session_state["user_submissions"]:
            df_my = pd.DataFrame(st.session_state["user_submissions"])
            df_my["default_probability"] = (df_my["default_probability"] * 100).round(1).astype(str) + "%"
            st.dataframe(
                df_my.rename(columns={
                    "id": "Log ID",
                    "applicant_name": "Borrower",
                    "credit_amount": "Amount (DM)",
                    "duration_months": "Term (Mo)",
                    "default_probability": "Default Risk",
                    "decision": "Decision",
                    "created_at": "Timestamp (UTC)"
                }),
                width="stretch"
            )
        else:
            st.info("No applications evaluated in this session.")

    else:
        st.caption("Authorized access required under GLBA and Fair Lending governance frameworks.")
        
        officer_key = st.text_input(
            "Authorization Key",
            type="password",
            placeholder="••••••••",
            help="Restricted to institutional risk officers and compliance auditors."
        )

        if officer_key == "riskflow2026":
            st.success("Clearance Authenticated: Institutional Audit Log Decrypted")
            try:
                audit_resp = requests.get(f"{API_URL}/api/v1/audit-trail?limit=100")
                if audit_resp.status_code == 200:
                    logs = audit_resp.json()
                    if logs:
                        df_logs = pd.DataFrame(logs)
                        df_logs["created_at"] = pd.to_datetime(df_logs["created_at"]).dt.strftime('%Y-%m-%d %H:%M:%S')
                        df_logs["default_probability"] = (df_logs["default_probability"] * 100).round(1).astype(str) + "%"
                        df_logs["applicant_name"] = df_logs["applicant_name"].apply(mask_name)

                        st.dataframe(
                            df_logs.rename(columns={
                                "id": "Audit ID",
                                "applicant_name": "Borrower (Masked PII)",
                                "credit_amount": "Amount (DM)",
                                "duration_months": "Term (Mo)",
                                "default_probability": "Risk Score",
                                "decision": "Decision",
                                "created_at": "Timestamp (UTC)"
                            }),
                            width="stretch"
                        )
                    else:
                        st.info("Database contains no registered decisions.")
            except Exception:
                st.error("Unable to query institutional ledger.")
        elif officer_key != "":
            st.error("Authentication Failed: Invalid authorization key.")
