from pydantic import BaseModel

# The standard data we expect when someone adds an AI model
class ModelBase(BaseModel):
    name: str
    provider: str
    cost_per_1k_tokens: float

# Schema for creating a model
class ModelCreate(ModelBase):
    pass

# Schema for returning a model (includes the auto-generated ID)
class ModelResponse(ModelBase):
    id: int

    class Config:
        from_attributes = True