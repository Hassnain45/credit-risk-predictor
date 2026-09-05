# 🏦 RiskFlow: Explainable Credit Underwriting & Risk Scoring System

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hassnain-credit-risk.streamlit.app/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.63+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-Cost--Optimized-EB5424)](https://xgboost.readthedocs.io/)
[![SHAP](https://img.shields.io/badge/SHAP-FCRA%20Compliant-blue)](https://shap.readthedocs.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Audit%20Ledger-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org)

An end-to-end, regulatory-compliant credit underwriting microservice featuring cost-sensitive threshold optimization, SHAP-driven Fair Credit Reporting Act (FCRA) adverse action reason codes, counterfactual recourse recommendations, and role-based audit governance.

🔗 **Live Portal**: [https://hassnain-credit-risk.streamlit.app/](https://hassnain-credit-risk.streamlit.app/)

---

## 📌 Problem & Business Context

In commercial banking, deploying machine learning models with default 50% classification cutoffs leads to major financial loss and regulatory violations:

1. **The Cost Asymmetry Problem**: Approving a borrower who defaults (False Negative) costs an institution an estimated **$5,000** in unrecoverable principal, while denying a qualified applicant (False Positive) results in only **$1,000** of lost interest income. Optimizing for raw accuracy ignores this 5:1 loss asymmetry.
2. **The Compliance & Explainability Mandate**: Consumer lending regulations (e.g., U.S. Fair Credit Reporting Act § 615(a) and EU AI Act Article 14) prohibit black-box algorithmic decisions. Lenders must supply legally defensible, actionable **Adverse Action Reason Codes** to every declined applicant.

**RiskFlow** bridges this gap by calibrating gradient boosted trees against an asymmetric cost matrix, extracting local Shapley marginals for regulatory compliance, and maintaining an immutable audit ledger with PII masking.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (UI Tier)                       │
│     RiskFlow Underwriting Desk (Streamlit + Custom CSS)     │
│  - Interactive Presets (Prime vs. Subprime Borrower)       │
│  - Session-Isolated Applications (Client Data Privacy)      │
│  - PIN-Gated Institutional Compliance Ledger (RBAC)         │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API (JSON / HTTP)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               BACKEND (FastAPI Microservice)                │
│  ├── Pydantic Schemas (Strict Request/Response Contracts)   │
│  ├── Cost-Calibrated Engine (Optimal Cutoff τ* = 18.0%)     │
│  ├── SHAP TreeExplainer (Adverse Action Extraction)         │
│  └── Counterfactual Recourse Simulation Engine              │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy ORM
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                DATABASE (Persistence Tier)                  │
│  └── SQLite (credit_underwriting.db)                        │
│      - Historical application logs & predicted probabilities│
│      - Automated PII masking for GDPR / GLBA compliance     │
└─────────────────────────────────────────────────────────────┘