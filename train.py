import json
import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

os.makedirs("models", exist_ok=True)

# 1. Fetch real UCI German Credit dataset
print("[1/4] Fetching UCI German Credit dataset from OpenML...")
raw = fetch_openml("credit-g", version=1, as_frame=True)
df = raw.frame

# Binary Target: 'bad' credit risk = 1 (Default), 'good' = 0
df["target"] = (df["class"] == "bad").astype(int)
X = df.drop(columns=["class", "target"])
y = df["target"]

# 2. Pipeline setup
print("[2/4] Preprocessing features...")
num_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
cat_cols = X.select_dtypes(include=["category", "object"]).columns.tolist()

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

encoded_cats = preprocessor.named_transformers_["cat"].get_feature_names_out(cat_cols)
feature_names = num_cols + list(encoded_cats)

# 3. Benchmark Models
print("[3/4] Training Logistic Regression, Random Forest, and XGBoost...")
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42, class_weight="balanced"),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42, eval_metric="logloss"),
}

metrics = {}
for name, clf in models.items():
    clf.fit(X_train_proc, y_train)
    preds = clf.predict(X_test_proc)
    probs = clf.predict_proba(X_test_proc)[:, 1]
    
    metrics[name] = {
        "ROC-AUC": round(float(roc_auc_score(y_test, probs)), 4),
        "F1-Score": round(float(f1_score(y_test, preds)), 4),
    }

# 4. Save Production Artifacts
print("[4/4] Saving model artifacts to /models...")
joblib.dump(preprocessor, "models/preprocessor.pkl")
joblib.dump(models["XGBoost"], "models/xgb_model.pkl")
joblib.dump(feature_names, "models/feature_names.pkl")

with open("models/model_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("\nSuccess! Generated artifacts in 'models/':")
for file in os.listdir("models"):
    print(f" - models/{file}")