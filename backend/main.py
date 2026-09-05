import json
import traceback
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database import get_db, engine as db_engine, Base
from backend.db_models import LoanApplication
from backend.schemas import LoanApplicationRequest, UnderwritingResponse, AuditTrailResponse
from backend.ml_engine import UnderwritingEngine

# Automatically initialize SQLite table schemas on boot
Base.metadata.create_all(bind=db_engine)

app = FastAPI(
    title="RiskFlow - Credit Underwriting API",
    description="Regulatory-compliant credit scoring microservice.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = UnderwritingEngine()

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "model_version": engine.config["model_version"], "threshold": engine.threshold}

@app.post("/api/v1/underwrite", response_model=UnderwritingResponse, tags=["Underwriting"])
def evaluate_application(payload: LoanApplicationRequest, db: Session = Depends(get_db)):
    try:
        data = payload.dict()
        eval_result = engine.evaluate(data)

        db_entry = LoanApplication(
            applicant_name=payload.applicant_name,
            duration_months=payload.duration_months,
            credit_amount=payload.credit_amount,
            installment_rate=payload.installment_rate,
            age=payload.age,
            checking_status=payload.checking_status,
            credit_history=payload.credit_history,
            savings_status=payload.savings_status,
            employment=payload.employment,
            purpose=payload.purpose,
            housing=payload.housing,
            default_probability=eval_result["default_probability"],
            decision=eval_result["decision"],
            optimal_threshold=eval_result["threshold_applied"],
            adverse_action_reasons=json.dumps(eval_result["adverse_action_reasons"]),
            model_version=eval_result["model_version"]
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)

        return UnderwritingResponse(
            application_id=db_entry.id,
            applicant_name=db_entry.applicant_name,
            probability_of_default=eval_result["default_probability"],
            decision=eval_result["decision"],
            threshold_applied=eval_result["threshold_applied"],
            adverse_action_reasons=eval_result["adverse_action_reasons"],
            counterfactual_recommendations=eval_result["counterfactual_recommendations"],
            model_version=eval_result["model_version"]
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )

@app.get("/api/v1/audit-trail", response_model=List[AuditTrailResponse], tags=["Audit"])
def get_audit_trail(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(LoanApplication).order_by(LoanApplication.created_at.desc()).limit(limit).all()
    return records
