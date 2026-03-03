from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI(
    title="AI-Model Router API",
    description="Intelligent routing gateway for AI models",
    version="1.0.0"
)

@app.get("/")
async def health_check():
    """
    Basic health check endpoint to verify the server is running.
    """
    return {
        "status": "online", 
        "message": "The AI Router Engine is active and listening."
    }