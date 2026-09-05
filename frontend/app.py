import os
import subprocess
import time
import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

def start_backend_daemon():
    try:
        requests.get(f"{API_URL}/health", timeout=1)
    except Exception:
        subprocess.Popen(
            ["uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
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

st.title("🏦 RiskFlow - Credit Underwriting Portal")
st.caption("Decoupled microservice architecture: FastAPI + SQLite + Cost-Optimized XGBoost + SHAP Explainability")

# Status check
try:
    health = requests.get(f"{API_URL}/health", timeout=2).json()
    st.sidebar.success(f"Backend: Online ({health['model_version']})")
    st.sidebar.info(f"Optimal Cutoff (tau*): {health['threshold']*100:.1f}%")
except Exception:
    st.sidebar.error("Backend initializing... please refresh in a moment.")

tab_underwrite, tab_audit = st.tabs(["📝 New Loan Application", "📋 Regulatory Audit Trail"])

with tab_underwrite:
    with st.form("loan_application_form"):
        st.subheader("Applicant Financial Profile")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            applicant_name = st.text_input("Applicant Name", value="Alex Morgan")
            duration_months = st.slider("Loan Duration (months)", min_value=4, max_value=72, value=36)
            credit_amount = st.number_input("Credit Amount (DM)", min_value=250, max_value=20000, value=4500, step=100)
            installment_rate = st.slider("Installment Rate (% of disposable income)", 1, 4, 3)

        with col2:
            age = st.slider("Age (years)", 18, 75, 29)
            checking_status = st.selectbox(
                "Checking Account Status",
                ["<0", "0<=X<200", ">=200", "no checking"],
                index=0
            )
            credit_history = st.selectbox(
                "Credit History",
                ["critical/other existing credit", "delayed previously", "existing paid", "all paid", "no credits/all paid"],
                index=1
            )
            savings_status = st.selectbox(
                "Savings Account Status",
                ["<100", "100<=X<500", "500<=X<1000", ">=1000", "no known savings"],
                index=0
            )

        with col3:
            employment = st.selectbox(
                "Employment Duration",
                ["unemployed", "<1", "1<=X<4", "4<=X<7", ">=7"],
                index=1
            )
            housing = st.selectbox("Housing Type", ["rent", "own", "for free"], index=0)
            purpose = st.selectbox(
                "Loan Purpose",
                ["new car", "used car", "furniture/equipment", "radio/tv", "domestic appliance", "repairs", "education", "business", "other"],
                index=0
            )
            residence_since = st.slider("Years at Present Residence", 1, 4, 2)

        submit_btn = st.form_submit_button("Submit for Underwriting", use_container_width=True)

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

        with st.spinner("Processing application via FastAPI microservice..."):
            try:
                resp = requests.post(f"{API_URL}/api/v1/underwrite", json=payload)
                if resp.status_code == 200:
                    result = resp.json()
                    
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
                            st.caption("Prescriptive scenario adjustments to flip decision to Approved:")
                            for cf in result["counterfactual_recommendations"]:
                                st.info(f"💡 {cf}")
                        else:
                            st.success("Applicant satisfies cost-optimized risk requirements.")
                            st.balloons()
                else:
                    st.error(f"API Error {resp.status_code}: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to FastAPI backend.")

with tab_audit:
    st.subheader("Immutable Underwriting Audit Logs")
    st.caption("Real-time loan decisions logged to SQLite database via backend ORM.")
    
    if st.button("Refresh Audit Logs", use_container_width=False):
        st.rerun()

    try:
        audit_resp = requests.get(f"{API_URL}/api/v1/audit-trail?limit=100")
        if audit_resp.status_code == 200:
            logs = audit_resp.json()
            if logs:
                df_logs = pd.DataFrame(logs)
                df_logs["created_at"] = pd.to_datetime(df_logs["created_at"]).dt.strftime('%Y-%m-%d %H:%M:%S')
                df_logs["default_probability"] = (df_logs["default_probability"] * 100).round(1).astype(str) + "%"
                st.dataframe(
                    df_logs.rename(columns={
                        "id": "Log ID",
                        "applicant_name": "Applicant",
                        "credit_amount": "Amount (DM)",
                        "duration_months": "Duration (Mo)",
                        "default_probability": "Default Risk",
                        "decision": "Decision",
                        "created_at": "Logged At"
                    }),
                    use_container_width=True
                )
            else:
                st.info("No applications logged in the database yet.")
        else:
            st.error("Failed to fetch audit records.")
    except requests.exceptions.ConnectionError:
        st.error("Backend offline. Cannot load audit trail.")
