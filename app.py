from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="My Custom Connector",
    version="1.0.0",
    description="A simple FastAPI service for ChatGPT Connector demo."
)

class HelloRequest(BaseModel):
    name: str

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/hello")
def say_hello(req: HelloRequest):
    return {"message": f"Hello, {req.name}! Your MCP test works perfectly."}

@app.get("/")
def home():
    return {"message": "MCP test service is running successfully!"}
