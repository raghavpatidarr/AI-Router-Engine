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
    db_model.specialty = updated_model.specialty  # <--- Added this to update specialty!
    
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


# --- THE AI ROUTER ENGINE ---

@app.post("/route/", response_model=schemas.RouterResponse)
def route_prompt(request: schemas.PromptRequest, db: Session = Depends(get_db)):
    
    prompt = request.user_prompt.lower()
    total_marks = 0
    detected_specialty = "general" # Default fallback
    
    # --- 1. THE EVALUATION ENGINE ---
 # --- 1. THE EVALUATION ENGINE ---
    
    # Split the prompt into a list of individual words so "fast" doesn't match "fastapi"
    words = prompt.replace(".", "").replace(",", "").split()
    
    tech_keywords = ["code", "python", "fastapi", "sql", "database", "docker", "react", "script"]
    if any(kw in words for kw in tech_keywords):  # <--- Changed prompt to words
        total_marks += 4  
        detected_specialty = "coding" 
        
    reasoning_keywords = ["explain", "analyze", "debug", "calculate", "logic", "compare", "why"]
    if any(kw in words for kw in reasoning_keywords): # <--- Changed prompt to words
        total_marks += 3
        if detected_specialty != "coding": 
            detected_specialty = "reasoning"
            
    speed_keywords = ["fast", "quick", "urgent", "short", "tl;dr", "brief"]
    if any(kw in words for kw in speed_keywords): # <--- Changed prompt to words
        total_marks -= 3 
        # Only override to general if it wasn't already marked as a coding or reasoning task
        if detected_specialty not in ["coding", "reasoning"]:
            detected_specialty = "general"
        
    # --- 2. SPECIALTY ROUTING ---
    # Find the model that perfectly matches our detected specialty
    selected_model = db.query(models.AIModel).filter(models.AIModel.specialty == detected_specialty).first()

    # Safety fallback if the database is empty
    if not selected_model:
        # Fallback to just grabbing any model if the specific specialty isn't found
        selected_model = db.query(models.AIModel).first()
        if not selected_model:
             return {"error": "No AI models found in the database."}
    
    reason = f"Routed to '{detected_specialty}' model. (Score: {total_marks})"

    # --- 3. THE API CONNECTION ---
    if selected_model.provider.lower() == "groq":
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": request.user_prompt}],
            model=selected_model.name,
        )
        ai_response = chat_completion.choices[0].message.content
    else:
        ai_response = f"Simulation: Sent to {selected_model.name}."

    return {
        "selected_model": selected_model.name,
        "provider": selected_model.provider,
        "cost": selected_model.cost_per_1k_tokens,
        "specialty": selected_model.specialty,
        "message": f"[{reason}]\n\n{ai_response}"
    }