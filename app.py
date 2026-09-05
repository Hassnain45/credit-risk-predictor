import json
import joblib
import matplotlib.pyplot as plt
import pandas as pd
import shap
import streamlit as st

st.set_page_config(
    page_title="Credit Risk & Explainability Engine",
    page_icon="💳",
    layout="wide",
)

# 1. Load Artifacts
@st.cache_resource
def load_artifacts():
    preprocessor = joblib.load("models/preprocessor.pkl")
    model = joblib.load("models/xgb_model.pkl")
    feature_names = joblib.load("models/feature_names.pkl")
    with open("models/model_metrics.json") as f:
        metrics = json.load(f)
    explainer = shap.TreeExplainer(model)
    return preprocessor, model, feature_names, metrics, explainer

preprocessor, model, feature_names, metrics, explainer = load_artifacts()

st.title("Credit Risk Predictor & Explainability Engine")
st.markdown(
    "Predict default probability on applicant profiles and visualize the exact risk drivers via **SHAP (SHapley Additive exPlanations)**."
)

# 2. Sidebar - Applicant Profile Inputs
st.sidebar.header("Applicant Financial Profile")

duration = st.sidebar.slider("Loan Duration (months)", min_value=4, max_value=72, value=24)
credit_amount = st.sidebar.number_input("Credit Amount (DM)", min_value=250, max_value=20000, value=3500, step=100)
installment_rate = st.sidebar.slider("Installment Rate (% of income)", min_value=1, max_value=4, value=2)
age = st.sidebar.slider("Age (years)", min_value=18, max_value=75, value=30)
residence_since = st.sidebar.slider("Years at Current Residence", min_value=1, max_value=4, value=2)
existing_credits = st.sidebar.slider("Number of Existing Credits at Bank", min_value=1, max_value=4, value=1)
num_dependents = st.sidebar.selectbox("Number of Dependents", [1, 2], index=0)

checking_status = st.sidebar.selectbox(
    "Checking Account Status",
    ["<0", "0<=X<200", ">=200", "no checking"],
    index=1,
)
credit_history = st.sidebar.selectbox(
    "Credit History",
    [
        "critical/other existing credit",
        "delayed previously",
        "existing paid",
        "all paid",
        "no credits/all paid",
    ],
    index=2,
)
savings_status = st.sidebar.selectbox(
    "Savings Account Status",
    ["<100", "100<=X<500", "500<=X<1000", ">=1000", "no known savings"],
    index=0,
)
employment = st.sidebar.selectbox(
    "Employment Duration",
    ["unemployed", "<1", "1<=X<4", "4<=X<7", ">=7"],
    index=2,
)
housing = st.sidebar.selectbox("Housing Type", ["rent", "own", "for free"], index=1)
purpose = st.sidebar.selectbox(
    "Loan Purpose",
    [
        "radio/tv",
        "education",
        "furniture/equipment",
        "new car",
        "used car",
        "business",
        "domestic appliance",
        "repairs",
        "other",
    ],
    index=3,
)

# Default fields for remaining schema features
applicant_raw = {
    "duration": [duration],
    "credit_amount": [credit_amount],
    "installment_commitment": [installment_rate],
    "residence_since": [residence_since],
    "age": [age],
    "existing_credits": [existing_credits],
    "num_dependents": [num_dependents],
    "checking_status": [checking_status],
    "credit_history": [credit_history],
    "purpose": [purpose],
    "savings_status": [savings_status],
    "employment": [employment],
    "personal_status": ["male single"],
    "other_parties": ["none"],
    "property_magnitude": ["car"],
    "other_payment_plans": ["none"],
    "housing": [housing],
    "job": ["skilled"],
    "own_telephone": ["yes"],
    "foreign_worker": ["yes"],
}

input_df = pd.DataFrame(applicant_raw)
input_proc = preprocessor.transform(input_df)

# 3. Main Dashboard Layout
col_pred, col_shap = st.columns([1, 1.2])

with col_pred:
    st.subheader("Model Evaluation Benchmark")
    benchmark_df = pd.DataFrame(metrics).T
    st.dataframe(benchmark_df.style.highlight_max(axis=0, color="#c6f6d5"))

    st.markdown("---")
    st.subheader("Inference Result")
    
    prob_default = float(model.predict_proba(input_proc)[0, 1])
    threshold = 0.50
    
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric(label="Probability of Default (PD)", value=f"{prob_default * 100:.1f}%")
    with col_metric2:
        if prob_default >= threshold:
            st.error("Decision: REJECT (High Risk)")
        else:
            st.success("Decision: APPROVE (Low Risk)")

    st.progress(min(prob_default, 1.0))
    st.caption(f"Decision threshold set at {int(threshold * 100)}% default risk.")

with col_shap:
    st.subheader("Local SHAP Attribution")
    st.caption("Features pushing risk up (red) vs. lowering risk (blue):")

    shap_vals = explainer(input_proc)
    shap_vals.feature_names = feature_names

    fig, ax = plt.subplots(figsize=(8, 5.5))
    shap.plots.waterfall(shap_vals[0], max_display=8, show=False)
    plt.tight_layout()
    st.pyplot(fig)