# 🏦 RiskFlow: Explainable Credit Underwriting & Risk-Based Pricing System

[![Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hassnain-credit-risk.streamlit.app/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.63+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![XGBoost](https://img.shields.io/badge/XGBoost-Cost--Calibrated-EB5424)](https://xgboost.readthedocs.io/)
[![SHAP](https://img.shields.io/badge/SHAP-FCRA%20Compliant-blue)](https://shap.readthedocs.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Audit%20Ledger-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org)

An institutional-grade credit decisioning engine that unifies cost-sensitive machine learning, Fair Credit Reporting Act (FCRA) adverse action attribution, parametric counterfactual recourse, dynamic risk-based APR pricing, and role-based audit privacy.

🔗 **Live Production Portal**: [https://hassnain-credit-risk.streamlit.app/](https://hassnain-credit-risk.streamlit.app/)

---

## 📌 Problem & Commercial Context

Conventional automated underwriting models fail in commercial lending due to three systemic gaps:

1. **The Cost Asymmetry Problem**: Approving a borrower who defaults (False Negative) costs the institution ~$5,000 in unrecoverable principal, whereas declining a creditworthy applicant (False Positive) forfeits ~$1,000 in net interest margin. Optimizing models for raw classification accuracy or standard 0.5 probability thresholds ignores this 5:1 financial penalty.
2. **The Compliance & Explainability Mandate**: Financial regulations (U.S. FCRA § 615(a) and EU AI Act Article 14) prohibit black-box automated credit denials. Lenders are legally required to provide specific, defensible **Adverse Action Reason Codes** alongside actionable recovery pathways.
3. **The Risk-Adjusted Pricing Gap**: Real banks do not issue flat yes/no verdicts to prime borrowers. Qualified loans must be priced against risk-adjusted return on capital (RAROC) to ensure interest margins offset expected portfolio loss.

**RiskFlow** addresses all three challenges by marrying cost-calibrated gradient boosting with local SHAP explainability, an automated APR pricing engine, and a privacy-preserving audit trail.

---

## 📐 Mathematical Formulation

### 1. Cost-Sensitive Threshold Optimization ($\tau^* = 18.0\%$)
The decision boundary is empirically calibrated by minimizing the institutional financial loss function on holdout test observations:

$$\mathcal{L}(\tau) = C_{\text{FN}} \cdot \sum_{i} \mathbb{I}(y_i = 1, \hat{p}_i < \tau) + C_{\text{FP}} \cdot \sum_{i} \mathbb{I}(y_i = 0, \hat{p}_i \ge \tau)$$

Where $C_{\text{FN}} = \$5,000$, $C_{\text{FP}} = \$1,000$, and $\hat{p}_i$ is the predicted probability of default ($PD$). Across an empirical grid sweep $\tau \in [0.10, 0.90]$, total institutional loss is minimized at **$\tau^* = 18.0\%$**.

### 2. Risk-Based APR Pricing Engine
For approved applicants ($\hat{p}_i < \tau^*$), the engine calculates an individualized annual percentage rate (APR) across three risk tiers:

* **Tier 1 (Prime Preferred, $PD < 6\%$):** $\text{APR} = 5.5\% + (PD \times 25.0)$
* **Tier 2 (Prime Standard, $6\% \le PD < 12\%$):** $\text{APR} = 7.0\% + (PD \times 28.0)$
* **Tier 3 (Near-Prime, $12\% \le PD \le 18\%$):** $\text{APR} = 10.5\% + (PD \times 25.0)$

### 3. Loan Amortization Schedule
Monthly debt obligation and total cumulative interest are calculated using standard fixed-rate amortization:

$$\text{Monthly Payment} (M) = P \cdot \frac{r(1 + r)^n}{(1 + r)^n - 1}$$

$$\text{Total Interest} = (M \cdot n) - P$$

Where $P$ is credit amount (principal), $r = \frac{\text{APR}}{12}$ is monthly interest rate, and $n$ is facility term in months.

---

## 🏗️ System Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                     FRONTEND (UI Tier)                        │
│          Streamlit Institutional Desk (Dark / Light)          │
│  - 1-Click Prime & Subprime Dynamic Presets                   │
│  - Live Underwriting Metrics & Policy Progress Gauge          │
│  - Session-Isolated History & PIN-Gated Audit Ledger          │
└───────────────────────────────┬───────────────────────────────┘
                                │ REST API (HTTP / JSON)
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                BACKEND (FastAPI Microservice)                 │
│  ├── Pydantic Schemas (Strict Request / Response Validation)  │
│  ├── Cost-Calibrated Decision Engine (τ* = 18.0%)             │
│  ├── SHAP TreeExplainer (Local Adverse Action Extraction)     │
│  ├── Parametric Counterfactual Recourse Generator             │
│  └── Dynamic Risk-Based Pricing Engine (APR & Amortization)   │
└───────────────────────────────┬───────────────────────────────┘
                                │ SQLAlchemy ORM
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                 DATABASE (Persistence Tier)                   │
│  └── SQLite (/tmp/credit_underwriting.db on Cloud)            │
│      - Historical underwriting decisions & default scores     │
│      - PII masking with authorized Underwriter unmask toggle  │
└───────────────────────────────────────────────────────────────┘