from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class LoanApplicationRequest(BaseModel):
    applicant_name: str = Field(default="Jane Doe", description="Applicant identifier")
    duration_months: int = Field(..., ge=4, le=72, example=24)
    credit_amount: float = Field(..., ge=250, le=20000, example=3500.0)
    installment_rate: int = Field(..., ge=1, le=4, example=2)
    age: int = Field(..., ge=18, le=80, example=32)
    residence_since: int = Field(default=2, ge=1, le=4)
    existing_credits: int = Field(default=1, ge=1, le=4)
    num_dependents: int = Field(default=1, ge=1, le=2)
    
    checking_status: str = Field(..., example="0<=X<200")
    credit_history: str = Field(..., example="existing paid")
    savings_status: str = Field(..., example="<100")
    employment: str = Field(..., example="1<=X<4")
    housing: str = Field(..., example="own")
    purpose: str = Field(..., example="new car")

class UnderwritingResponse(BaseModel):
    application_id: int
    applicant_name: str
    probability_of_default: float
    decision: str  # "APPROVED" or "REJECTED"
    threshold_applied: float
    adverse_action_reasons: List[str]
    counterfactual_recommendations: List[str]
    model_version: str

class AuditTrailResponse(BaseModel):
    id: int
    applicant_name: str
    credit_amount: float
    duration_months: int
    default_probability: float
    decision: str
    created_at: datetime

    class Config:
        from_attributes = True
