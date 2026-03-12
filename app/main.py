import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from groq import Groq

from .database import engine, get_db
from . import models, schemas

# Load the secret keys from your .env file
load_dotenv()

# Initialize the Groq Client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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

@app.post("/models/", response_model=schemas.ModelResponse)
def create_ai_model(model: schemas.ModelCreate, db: Session = Depends(get_db)):
    new_model = models.AIModel(**model.model_dump())
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return new_model

@app.get("/models/", response_model=list[schemas.ModelResponse])
def get_all_models(db: Session = Depends(get_db)):
    return db.query(models.AIModel).all()

# --- DATABASE MANAGEMENT DOORS ---

# Update an existing model (e.g., fixing a price)
@app.put("/models/{model_id}", response_model=schemas.ModelResponse)
def update_ai_model(model_id: int, updated_model: schemas.ModelCreate, db: Session = Depends(get_db)):
    # Find the model in the database by its ID
    db_model = db.query(models.AIModel).filter(models.AIModel.id == model_id).first()
    
    # If it doesn't exist, tell the user
    if not db_model:
        return {"error": "Model not found"}
    
    # Update the details
    db_model.name = updated_model.name
    db_model.provider = updated_model.provider
    db_model.cost_per_1k_tokens = updated_model.cost_per_1k_tokens
    
    db.commit()
    db.refresh(db_model)
    return db_model

# Delete a broken model from the database
@app.delete("/models/{model_id}")
def delete_ai_model(model_id: int, db: Session = Depends(get_db)):
    # Find the model
    db_model = db.query(models.AIModel).filter(models.AIModel.id == model_id).first()
    
    if not db_model:
        return {"error": "Model not found"}
    
    # Destroy it
    db.delete(db_model)
    db.commit()
    return {"message": f"Successfully deleted model ID {model_id}"}

# --- THE UPGRADED ROUTER ---
@app.post("/route/", response_model=schemas.RouterResponse)
def route_prompt(request: schemas.PromptRequest, db: Session = Depends(get_db)):
    
    # 1. Find the cheapest model in the PostgreSQL database
    cheapest_model = db.query(models.AIModel).order_by(models.AIModel.cost_per_1k_tokens.asc()).first()
    
    if not cheapest_model:
        return {"error": "No AI models found in the database. Please add some first!"}
    
    # 2. If the cheapest model is from Groq, actually send the prompt to the AI!
    if cheapest_model.provider.lower() == "groq":
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": request.user_prompt}],
            model=cheapest_model.name,
        )
        # Extract the actual text response from the AI
        ai_response = chat_completion.choices[0].message.content
    else:
        # Fallback if it's not Groq
        ai_response = f"Simulation: I would route this to {cheapest_model.name}, but I only have keys for Groq right now!"

    # 3. Return the final data and the AI's actual answer
    return {
        "selected_model": cheapest_model.name,
        "provider": cheapest_model.provider,
        "cost": cheapest_model.cost_per_1k_tokens,
        "message": ai_response
    }