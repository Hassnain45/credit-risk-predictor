from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from backend.database import Base

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_name = Column(String(100), default="Anonymous")
    duration_months = Column(Integer, nullable=False)
    credit_amount = Column(Float, nullable=False)
    installment_rate = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    checking_status = Column(String(50), nullable=False)
    credit_history = Column(String(50), nullable=False)
    savings_status = Column(String(50), nullable=False)
    employment = Column(String(50), nullable=False)
    purpose = Column(String(50), nullable=False)
    housing = Column(String(50), nullable=False)
    
    # Underwriting Decision Outputs
    default_probability = Column(Float, nullable=False)
    decision = Column(String(20), nullable=False)  # APPROVED or REJECTED
    optimal_threshold = Column(Float, nullable=False)
    adverse_action_reasons = Column(Text, nullable=True)  # JSON or comma-separated top SHAP risk drivers
    model_version = Column(String(50), default="xgb-v1.0")
    created_at = Column(DateTime, default=datetime.utcnow)