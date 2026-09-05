import os
import sys
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

# ---------------------------------------------------------------------------
# THEME STATE
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

def toggle_theme():
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"

is_dark = st.session_state["theme"] == "dark"

if is_dark:
    C_BG = "#0B0F14"
    C_BG_ALT = "#111823"
    C_SURFACE = "#151D28"
    C_SURFACE_HOVER = "#1B2530"
    C_TEXT = "#F8FAFC"             # Crisp high-contrast off-white
    C_TEXT_MUTED = "#94A3B8"       # Clear slate silver
    C_BORDER = "rgba(255,255,255,0.10)"
    C_PRIMARY = "#F5B93F"          # Amber gold
    C_PRIMARY_SOFT = "rgba(245, 185, 63, 0.16)"
    C_ACCENT = "#2DD4A7"           # Emerald teal
    C_ACCENT_SOFT = "rgba(45, 212, 167, 0.16)"
    C_DANGER = "#FF6B6B"
    C_DANGER_SOFT = "rgba(255, 107, 107, 0.16)"
    C_SUCCESS = "#2DD4A7"
    C_SUCCESS_SOFT = "rgba(45, 212, 167, 0.16)"
    C_SHADOW = "0 8px 30px rgba(0,0,0,0.45)"
else:
    C_BG = "#FBF8F2"
    C_BG_ALT = "#F3EEE3"
    C_SURFACE = "#FFFFFF"
    C_SURFACE_HOVER = "#FBF3E3"
    C_TEXT = "#0F172A"             # Crisp deep slate
    C_TEXT_MUTED = "#475569"       # High-contrast readable charcoal
    C_BORDER = "rgba(29,36,48,0.12)"
    C_PRIMARY = "#C9861A"          # Amber gold
    C_PRIMARY_SOFT = "rgba(201, 134, 26, 0.14)"
    C_ACCENT = "#0E9F76"           # Emerald teal
    C_ACCENT_SOFT = "rgba(14, 159, 118, 0.14)"
    C_DANGER = "#DC2626"
    C_DANGER_SOFT = "rgba(220, 38, 38, 0.12)"
    C_SUCCESS = "#0E9F76"
    C_SUCCESS_SOFT = "rgba(14, 159, 118, 0.12)"
    C_SHADOW = "0 8px 24px rgba(29,36,48,0.10)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        transition: background-color 0.4s ease, color 0.4s ease;
    }}

    .stApp {{
        background: linear-gradient(160deg, {C_BG} 0%, {C_BG_ALT} 100%);
        color: {C_TEXT} !important;
    }}

    /* Global Text & Label Visibility Enforcement */
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp div[data-testid="stMarkdownContainer"] p,
    .stApp div[data-testid="stWidgetLabel"] label,
    .stApp div[data-testid="stWidgetLabel"] p,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp .stSelectbox label,
    .stApp .stSlider label,
    .stApp .stTextInput label,
    .stApp .stNumberInput label,
    .stApp div[data-baseweb="radio"] label,
    .stApp div[data-testid="stRadio"] label p,
    .stApp div[data-testid="stMetricValue"] {{
        color: {C_TEXT} !important;
    }}

    /* Inputs, Selectboxes & Sliders */
    .stTextInput input, 
    .stNumberInput input,
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] span {{
        color: {C_TEXT} !important;
        background-color: {C_BG_ALT} !important;
        border: 1px solid {C_BORDER} !important;
    }}

    /* Muted Labels & Captions */
    .stCaption, 
    .stCaption p, 
    small, 
    .rf-hero p,
    .rf-hero-tag,
    div[data-testid="stMetricLabel"] label,
    div[data-testid="stMetricLabel"] p {{
        color: {C_TEXT_MUTED} !important;
    }}

    h1, h2, h3, .stTitle {{
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
        color: {C_TEXT} !important;
    }}

    section[data-testid="stSidebar"] {{
        background: {C_SURFACE};
        border-right: 1px solid {C_BORDER};
    }}

    /* Animations */
    @keyframes fadeSlideIn {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes pulseGlow {{
        0%, 100% {{ box-shadow: 0 0 0 0 rgba(245, 185, 63, 0.35); }}
        50% {{ box-shadow: 0 0 0 8px rgba(245, 185, 63, 0); }}
    }}
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .block-container {{
        animation: fadeSlideIn 0.5s ease-out;
        padding-top: 2rem;
    }}

    /* Hero Header */
    .rf-hero {{
        background: linear-gradient(120deg, {C_PRIMARY_SOFT}, {C_ACCENT_SOFT}, {C_PRIMARY_SOFT});
        background-size: 200% 200%;
        animation: gradientShift 10s ease infinite;
        border: 1px solid {C_BORDER};
        border-radius: 20px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: {C_SHADOW};
    }}
    .rf-hero h1 {{
        margin: 0;
        font-size: 2.1rem;
        background: linear-gradient(90deg, {C_PRIMARY}, {C_ACCENT});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent !important;
        background-clip: text;
    }}

    /* Status Badges */
    .status-badge {{
        display: inline-block;
        padding: 0.4rem 1.1rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        animation: pulseGlow 2.2s infinite;
        transition: transform 0.25s ease;
    }}
    .status-badge:hover {{ transform: scale(1.05); }}
    .badge-approved {{
        background: {C_SUCCESS_SOFT};
        color: {C_SUCCESS} !important;
        border: 1px solid {C_SUCCESS};
    }}
    .badge-rejected {{
        background: {C_DANGER_SOFT};
        color: {C_DANGER} !important;
        border: 1px solid {C_DANGER};
        animation: none;
    }}

    /* Info Boxes */
    .risk-driver-box {{
        background: {C_DANGER_SOFT};
        border-left: 3px solid {C_DANGER};
        color: {C_TEXT} !important;
        padding: 0.8rem 1.1rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 0.55rem;
        font-size: 0.9rem;
        transition: all 0.25s ease;
        animation: fadeSlideIn 0.4s ease-out;
    }}
    .risk-driver-box:hover {{
        transform: translateX(4px);
        box-shadow: {C_SHADOW};
    }}

    .action-box {{
        background: {C_ACCENT_SOFT};
        border-left: 3px solid {C_ACCENT};
        color: {C_TEXT} !important;
        padding: 0.8rem 1.1rem;
        border-radius: 0 12px 12px 0;
        margin-bottom: 0.55rem;
        font-size: 0.9rem;
        transition: all 0.25s ease;
        animation: fadeSlideIn 0.4s ease-out;
    }}
    .action-box:hover {{
        transform: translateX(4px);
        box-shadow: {C_SHADOW};
    }}

    /* Containers */
    div[data-testid="stForm"] {{
        background: {C_SURFACE};
        border: 1px solid {C_BORDER};
        border-radius: 18px;
        padding: 1.6rem;
        box-shadow: {C_SHADOW};
    }}

    div[data-testid="stMetric"] {{
        background: {C_SURFACE};
        border: 1px solid {C_BORDER};
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: {C_SHADOW};
    }}

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button {{
        background: linear-gradient(90deg, {C_PRIMARY}, {C_ACCENT});
        color: #0B0F14 !important;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 14px {C_PRIMARY_SOFT};
        transition: transform 0.2s ease, filter 0.2s ease;
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        transform: translateY(-2px) scale(1.01);
        filter: brightness(1.08);
        box-shadow: {C_SHADOW};
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 1px solid {C_BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px 10px 0 0;
        padding: 0.6rem 1.2rem;
        color: {C_TEXT_MUTED} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: {C_PRIMARY_SOFT} !important;
        color: {C_PRIMARY} !important;
        font-weight: 700;
    }}

    /* Progress & Sliders */
    div[data-baseweb="slider"] > div > div {{
        background: linear-gradient(90deg, {C_ACCENT}, {C_PRIMARY}) !important;
    }}
    div[role="progressbar"] > div {{
        background: linear-gradient(90deg, {C_ACCENT}, {C_PRIMARY}) !important;
        transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }}

    /* Tables */
    div[data-testid="stDataFrame"] {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid {C_BORDER};
    }}

    hr {{ border-color: {C_BORDER} !important; }}
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
    parts = str(name).split()
    masked = [p[0] + "*" * (len(p) - 1) if len(p) > 1 else p for p in parts]
    return " ".join(masked)

with st.sidebar:
    st.title("⚖️ RiskFlow Engine")
    st.caption("Institutional Credit Decisioning Architecture")

    theme_label = "🌙 Dark Mode" if is_dark else "☀️ Light Mode"
    st.toggle(theme_label, value=is_dark, key="theme_toggle", on_change=toggle_theme)

    st.divider()

    try:
        health = requests.get(f"{API_URL}/health", timeout=2).json()
        st.success(f"Backend Active\nModel: `{health['model_version']}`")
        st.metric("Policy Tolerance (tau*)", f"{health['threshold']*100:.1f}%")
    except Exception:
        st.error("Connecting to scoring microservice...")

    st.divider()
    st.subheader("⚡ Interactive Profiles")
    st.caption("Load verified profiles to evaluate cutoff mechanics:")
    col_pre1, col_pre2 = st.columns(2)
    with col_pre1:
        st.button("🟢 Prime", on_click=set_prime_borrower, use_container_width=True)
    with col_pre2:
        st.button("🔴 Subprime", on_click=set_subprime_borrower, use_container_width=True)

st.markdown("""
<div class="rf-hero">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
            <h1>Credit Risk Underwriting Portal</h1>
            <p>Cost-Calibrated Gradient Boosting • SHAP FCRA Reason Codes • Automated Recourse</p>
        </div>
        <div class="rf-hero-tag">
            Regulatory Framework:<br>US FCRA § 615(a) / EU AI Act Article 14
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("ℹ️  About RiskFlow — What is this and why was it built?"):
    st.markdown(f"""
    **RiskFlow** is a credit risk underwriting simulation built to demonstrate how a real
    institutional lending desk could combine machine learning with regulatory-grade transparency.

    **What it does**
    - Scores a loan applicant's probability of default using a cost-calibrated gradient boosting model
    - Applies an institutional risk threshold (τ*) to convert that score into an APPROVE / DECLINE decision
    - Explains *why* using SHAP-based local attribution, in the same spirit as adverse-action notices
      required under **US FCRA § 615(a)**
    - Suggests concrete, actionable changes (counterfactual recourse) an applicant could make to
      flip a decline into an approval

    **Why it was built**
    Most credit-scoring demos stop at "here's a probability." Real lenders operating under fair-lending
    law can't do that — a decline has to come with a *reason*, and increasingly (under frameworks like
    the **EU AI Act, Article 14**) with human oversight and explainability baked in. This project exists
    to show that pipeline end-to-end: model → decision → explanation → recourse → audit trail, rather
    than just a bare classifier.

    **Who this is for**
    A portfolio/academic project exploring explainable AI (XAI) in a regulated, high-stakes domain —
    useful as a reference for anyone studying model governance, SHAP explainability, or building
    decision-support tools that need to justify themselves.
    """)

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

        submit_btn = st.form_submit_button("⚡ Run Decisioning Engine", use_container_width=True)

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
                    pd_score = float(res["probability_of_default"])
                    threshold = float(res["threshold_applied"])
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
                use_container_width=True
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
                            use_container_width=True
                        )
                    else:
                        st.info("Database contains no registered decisions.")
            except Exception:
                st.error("Unable to query institutional ledger.")
        elif officer_key != "":
            st.error("Authentication Failed: Invalid authorization key.")