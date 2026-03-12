from sqlalchemy import Column, Integer, String, Float
from .database import Base

class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    provider = Column(String)
    cost_per_1k_tokens = Column(Float)
    specialty = Column(String, default="general")  # <--- NEW COLUMN!