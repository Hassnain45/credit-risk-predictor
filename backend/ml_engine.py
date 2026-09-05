import os
import json
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

MODEL_DIR = "models"
CONFIG_PATH = os.path.join(MODEL_DIR, "underwriting_config.json")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessor.pkl")
MODEL_PATH = os.path.join(MODEL_DIR, "xgb_model.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "feature_names.pkl")

def train_and_calibrate():
    df = pd.read_csv("data/german_credit.csv")
    X = df.drop(columns=["target"])
    y = df["target"]

    num_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)

    cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(cat_cols)
    feature_names = num_cols + list(cat_feature_names)

    model = XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
        eval_metric="logloss"
    )
    model.fit(X_train_proc, y_train)

    test_probs = model.predict_proba(X_test_proc)[:, 1]
    thresholds = np.linspace(0.1, 0.9, 81)
    lowest_cost = float("inf")
    best_threshold = 0.50

    for tau in thresholds:
        preds = (test_probs >= tau).astype(int)
        fn = np.sum((y_test == 1) & (preds == 0))
        fp = np.sum((y_test == 0) & (preds == 1))
        cost = (fn * 5000) + (fp * 1000)
        if cost < lowest_cost:
            lowest_cost = cost
            best_threshold = round(float(tau), 2)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(feature_names, FEATURES_PATH)

    config = {
        "model_version": "xgb-v1.0-cost-optimized",
        "optimal_threshold": best_threshold,
        "cost_fn_weight": 5000,
        "cost_fp_weight": 1000
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

class UnderwritingEngine:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            train_and_calibrate()

        self.preprocessor = joblib.load(PREPROCESSOR_PATH)
        self.model = joblib.load(MODEL_PATH)
        self.feature_names = joblib.load(FEATURES_PATH)
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
        self.threshold = self.config["optimal_threshold"]
        self.explainer = shap.TreeExplainer(self.model)

    def _prepare_dataframe(self, data: dict) -> pd.DataFrame:
        row = {
            "duration": [data["duration_months"]],
            "credit_amount": [data["credit_amount"]],
            "installment_commitment": [data["installment_rate"]],
            "residence_since": [data.get("residence_since", 2)],
            "age": [data["age"]],
            "existing_credits": [data.get("existing_credits", 1)],
            "num_dependents": [data.get("num_dependents", 1)],
            "checking_status": [data["checking_status"]],
            "credit_history": [data["credit_history"]],
            "purpose": [data["purpose"]],
            "savings_status": [data["savings_status"]],
            "employment": [data["employment"]],
            "personal_status": ["male single"],
            "other_parties": ["none"],
            "property_magnitude": ["car"],
            "other_payment_plans": ["none"],
            "housing": [data["housing"]],
            "job": ["skilled"],
            "own_telephone": ["yes"],
            "foreign_worker": ["yes"]
        }
        return pd.DataFrame(row)

    def evaluate(self, applicant_data: dict):
        df_input = self._prepare_dataframe(applicant_data)
        proc_input = self.preprocessor.transform(df_input)
        pd_score = float(self.model.predict_proba(proc_input)[0, 1])

        decision = "REJECTED" if pd_score >= self.threshold else "APPROVED"

        # Adverse Action / SHAP Explanation with tensor dimension unpacking
        shap_vals = self.explainer(proc_input)
        raw_vals = shap_vals.values[0]

        if hasattr(raw_vals, "ndim") and raw_vals.ndim == 2:
            vals = raw_vals[:, 1]  # positive class (default)
        elif hasattr(raw_vals, "ndim") and raw_vals.ndim == 1:
            vals = raw_vals
        else:
            vals = np.array(raw_vals).flatten()

        feature_impacts = [(name, float(v)) for name, v in zip(self.feature_names, vals)]
        risk_drivers = sorted(feature_impacts, key=lambda x: x[1], reverse=True)

        adverse_reasons = []
        for name, val in risk_drivers[:3]:
            if val > 0:
                clean_name = name.replace("cat__", "").replace("num__", "").replace("_", " ").title()
                adverse_reasons.append(f"Elevated risk attributed to: {clean_name}")

        counterfactuals = []
        if decision == "REJECTED":
            if applicant_data["duration_months"] > 12:
                alt_data = dict(applicant_data)
                alt_data["duration_months"] = max(12, int(applicant_data["duration_months"] * 0.6))
                alt_df = self._prepare_dataframe(alt_data)
                alt_pd = float(self.model.predict_proba(self.preprocessor.transform(alt_df))[0, 1])
                if alt_pd < self.threshold:
                    counterfactuals.append(
                        f"Reduce loan term to {alt_data['duration_months']} months (estimated PD drops to {alt_pd*100:.1f}%)."
                    )

            alt_data_amount = dict(applicant_data)
            alt_data_amount["credit_amount"] = round(applicant_data["credit_amount"] * 0.75, 2)
            alt_amount_df = self._prepare_dataframe(alt_data_amount)
            alt_amount_pd = float(self.model.predict_proba(self.preprocessor.transform(alt_amount_df))[0, 1])
            if alt_amount_pd < self.threshold:
                counterfactuals.append(
                    f"Lower loan amount by 25% to DM {alt_data_amount['credit_amount']} (estimated PD drops to {alt_amount_pd*100:.1f}%)."
                )

            if not counterfactuals:
                counterfactuals.append("Provide a qualified co-guarantor or increase initial down payment.")

        return {
            "default_probability": round(pd_score, 4),
            "decision": decision,
            "threshold_applied": self.threshold,
            "adverse_action_reasons": adverse_reasons,
            "counterfactual_recommendations": counterfactuals,
            "model_version": self.config["model_version"]
        }
