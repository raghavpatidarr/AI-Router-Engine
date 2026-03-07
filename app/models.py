from sqlalchemy import Column, Integer, String, Float
from .database import Base

class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # e.g., "gpt-4o" or "claude-3"
    provider = Column(String)                      # e.g., "OpenAI" or "Anthropic"
    cost_per_1k_tokens = Column(Float)             # The price to help the router decide