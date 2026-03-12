from pydantic import BaseModel

# --- DATABASE SCHEMAS ---

class ModelBase(BaseModel):
    name: str
    provider: str
    cost_per_1k_tokens: float
    specialty: str = "general"  # <--- We added this!

class ModelCreate(ModelBase):
    pass

class ModelResponse(ModelBase):
    id: int
    class Config:
        from_attributes = True

# --- ROUTER SCHEMAS ---

class PromptRequest(BaseModel):
    user_prompt: str

class RouterResponse(BaseModel):
    selected_model: str
    provider: str
    cost: float
    specialty: str  # <--- We added this!
    message: str