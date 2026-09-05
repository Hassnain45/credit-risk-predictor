import os
import sys
import subprocess
import time
import uuid
import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

def start_backend_daemon():
    try:
        requests.get(f"{API_URL}/health", timeout=1)
    except Exception:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env = os.environ.copy()
        env["PYTHONPATH"] = root_dir

        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=root_dir,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(15):
            try:
                if requests.get(f"{API_URL}/health", timeout=1).status_code == 200:
                    break
            except Exception:
                time.sleep(1)

start_backend_daemon()

st.set_page_config(
    page_title="RiskFlow Underwriting Portal",
    page_icon="🏦",
    layout="wide"
)

# Initialize user session storage
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
        "name": "Sarah Connor (Prime)",
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
        "name": "Alex Morgan (Subprime)",
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

st.title("🏦 RiskFlow - Credit Underwriting Portal")
st.caption("Decoupled microservice architecture: FastAPI + SQLite + Cost-Optimized XGBoost + SHAP Explainability")

# Sidebar
try:
    health = requests.get(f"{API_URL}/health", timeout=2).json()
    st.sidebar.success(f"Backend: Online ({health['model_version']})")
    st.sidebar.info(f"Optimal Cutoff (tau*): {health['threshold']*100:.1f}%")
except Exception:
    st.sidebar.error("Backend initializing... please refresh.")

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ 1-Click Applicant Presets")
st.sidebar.caption("Test both approval and rejection outcomes instantly:")
st.sidebar.button("🟢 Load Prime Applicant (Approves)", on_click=set_prime_borrower, width="stretch")
st.sidebar.button("🔴 Load Subprime Applicant (Rejects)", on_click=set_subprime_borrower, width="stretch")

tab_underwrite, tab_audit = st.tabs(["📝 New Loan Application", "🔒 Regulatory Audit Trail"])

preset = st.session_state["preset_data"]

with tab_underwrite:
    with st.form("loan_application_form"):
        st.subheader("Applicant Financial Profile")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            applicant_name = st.text_input("Applicant Name", value=preset["name"])
            duration_months = st.slider("Loan Duration (months)", min_value=4, max_value=72, value=preset["duration"])
            credit_amount = st.number_input("Credit Amount (DM)", min_value=250, max_value=20000, value=preset["amount"], step=100)
            installment_rate = st.slider("Installment Rate (% of income)", 1, 4, preset["rate"])

        with col2:
            age = st.slider("Age (years)", 18, 75, preset["age"])
            checking_opts = [">=200", "0<=X<200", "<0", "no checking"]
            checking_status = st.selectbox("Checking Status", checking_opts, index=checking_opts.index(preset["checking"]))
            
            history_opts = ["all paid", "existing paid", "critical/other existing credit", "delayed previously", "no credits/all paid"]
            credit_history = st.selectbox("Credit History", history_opts, index=history_opts.index(preset["history"]))
            
            savings_opts = [">=1000", "500<=X<1000", "100<=X<500", "<100", "no known savings"]
            savings_status = st.selectbox("Savings Status", savings_opts, index=savings_opts.index(preset["savings"]))

        with col3:
            emp_opts = [">=7", "4<=X<7", "1<=X<4", "<1", "unemployed"]
            employment = st.selectbox("Employment Duration", emp_opts, index=emp_opts.index(preset["employment"]))
            
            housing_opts = ["own", "rent", "for free"]
            housing = st.selectbox("Housing Type", housing_opts, index=housing_opts.index(preset["housing"]))
            
            purpose_opts = ["new car", "used car", "business", "education", "repairs", "radio/tv", "furniture/equipment"]
            purpose = st.selectbox("Loan Purpose", purpose_opts, index=purpose_opts.index(preset["purpose"]))
            
            residence_since = st.slider("Years at Present Residence", 1, 4, preset["residence"])

        submit_btn = st.form_submit_button("Submit for Underwriting", width="stretch")

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

        with st.spinner("Analyzing credit risk via FastAPI microservice..."):
            try:
                resp = requests.post(f"{API_URL}/api/v1/underwrite", json=payload)
                if resp.status_code == 200:
                    result = resp.json()
                    
                    # Store in user's isolated session history
                    st.session_state["user_submissions"].insert(0, {
                        "id": result["application_id"],
                        "applicant_name": result["applicant_name"],
                        "credit_amount": credit_amount,
                        "duration_months": duration_months,
                        "default_probability": result["probability_of_default"],
                        "decision": result["decision"],
                        "created_at": pd.Timestamp.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    })

                    st.divider()
                    col_res1, col_res2 = st.columns([1, 1.2])

                    with col_res1:
                        st.subheader("Underwriting Decision")
                        decision_color = "red" if result["decision"] == "REJECTED" else "green"
                        st.markdown(f"### Result: :{decision_color}[{result['decision']}]")
                        
                        m_col1, m_col2 = st.columns(2)
                        m_col1.metric("Default Probability (PD)", f"{result['probability_of_default'] * 100:.1f}%")
                        m_col2.metric("Optimal Policy Cutoff", f"{result['threshold_applied'] * 100:.1f}%")
                        st.caption(f"Application Log ID: #{result['application_id']} | Model: {result['model_version']}")

                    with col_res2:
                        if result["decision"] == "REJECTED":
                            st.subheader("FCRA Adverse Action Reasons")
                            st.caption("Top risk drivers flagged by local SHAP interpretability:")
                            for reason in result["adverse_action_reasons"]:
                                st.error(f"- {reason}")
                            
                            st.subheader("Counterfactual Path to Approval")
                            st.caption("Adjustments to satisfy underwriter requirements:")
                            for cf in result["counterfactual_recommendations"]:
                                st.info(f"💡 {cf}")
                        else:
                            st.success("✅ Application Approved! Meets institutional risk and loss thresholds.")
                            st.balloons()
                else:
                    st.error(f"API Error: {resp.text}")
            except Exception as e:
                st.error("Failed to connect to FastAPI backend.")

with tab_audit:
    st.subheader("Underwriting Logs & Privacy Controls")
    
    view_mode = st.radio(
        "Select Access Level:",
        ["👤 My Session Applications (Private)", "🔑 Bank Compliance Officer Portal (Restricted)"],
        horizontal=True
    )

    if view_mode == "👤 My Session Applications (Private)":
        st.caption("Displays only decisions generated during your active browser session.")
        if st.session_state["user_submissions"]:
            df_my = pd.DataFrame(st.session_state["user_submissions"])
            df_my["default_probability"] = (df_my["default_probability"] * 100).round(1).astype(str) + "%"
            st.dataframe(
                df_my.rename(columns={
                    "id": "Log ID",
                    "applicant_name": "Applicant",
                    "credit_amount": "Amount (DM)",
                    "duration_months": "Term (Mo)",
                    "default_probability": "Default Risk",
                    "decision": "Decision",
                    "created_at": "Timestamp (UTC)"
                }),
                width="stretch"
            )
        else:
            st.info("You haven't submitted any applications during this session yet.")

    else:
        st.caption("Access to the complete institutional database requires underwriter authorization.")
        officer_key = st.text_input("Enter Underwriter Security PIN (Demo PIN: riskflow2026)", type="password")

        if officer_key == "riskflow2026":
            st.success("Authorization Verified: Underwriter Audit Mode Active")
            try:
                audit_resp = requests.get(f"{API_URL}/api/v1/audit-trail?limit=100")
                if audit_resp.status_code == 200:
                    logs = audit_resp.json()
                    if logs:
                        df_logs = pd.DataFrame(logs)
                        df_logs["created_at"] = pd.to_datetime(df_logs["created_at"]).dt.strftime('%Y-%m-%d %H:%M:%S')
                        df_logs["default_probability"] = (df_logs["default_probability"] * 100).round(1).astype(str) + "%"
                        
                        # Anonymize names to comply with privacy frameworks (GDPR / GLBA)
                        df_logs["applicant_name"] = df_logs["applicant_name"].apply(mask_name)

                        st.dataframe(
                            df_logs.rename(columns={
                                "id": "Log ID",
                                "applicant_name": "Applicant (Masked PII)",
                                "credit_amount": "Amount (DM)",
                                "duration_months": "Term (Mo)",
                                "default_probability": "Default Risk",
                                "decision": "Decision",
                                "created_at": "Timestamp (UTC)"
                            }),
                            width="stretch"
                        )
                    else:
                        st.info("No applications in database.")
            except Exception:
                st.error("Could not fetch database records.")
        elif officer_key != "":
            st.error("Invalid Underwriter PIN.")
