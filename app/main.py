from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schemas

# Build tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Model Router API",
    description="Intelligent routing gateway for AI models",
    version="1.0.0"
)

@app.get("/")
async def health_check():
    return {"status": "online", "message": "The AI Router Engine is active and listening."}

# --- NEW ENDPOINTS ---

# 1. Add a new AI Model to the Database
@app.post("/models/", response_model=schemas.ModelResponse)
def create_ai_model(model: schemas.ModelCreate, db: Session = Depends(get_db)):
    # Convert Pydantic schema to SQLAlchemy model
    new_model = models.AIModel(**model.model_dump())
    # Save to PostgreSQL
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return new_model

# 2. Get a list of all saved AI Models
@app.get("/models/", response_model=list[schemas.ModelResponse])
def get_all_models(db: Session = Depends(get_db)):
    return db.query(models.AIModel).all()