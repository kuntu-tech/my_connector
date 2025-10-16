from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="My Custom Connector",
    version="1.0.0",
    description="A simple FastAPI service for ChatGPT Connector demo.",
)

class HelloRequest(BaseModel):
    name: str

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Service is running"}

@app.post("/hello")
def say_hello(req: HelloRequest):
    return {"message": f"Hello, {req.name}. Your connector is working properly."}

@app.get("/")
def home():
    return {
        "message": "My Custom Connector is running successfully. Visit /docs for API documentation."
    }

@app.get("/health")
def health():
    return {"status": "ok"}
