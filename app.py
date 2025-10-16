from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
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

@app.post("/hello")
def say_hello(req: HelloRequest):
    return {"message": f"Hello, {req.name}! Your connector works fine."}

@app.get("/")
def home():
    return {"message": "Connector is running. Visit /docs for API info."}

@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    import json
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Return pretty-printed JSON (important!)
    return JSONResponse(content=json.loads(json.dumps(openapi_schema, indent=2)))
