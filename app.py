from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="My Custom Connector",
    version="1.0.0",
    description="A simple FastAPI service for ChatGPT Connector demo.",
)

# ---------- 数据模型 ----------
class HelloRequest(BaseModel):
    name: str

# ---------- 基础接口 ----------
@app.get("/ping")
def ping():
    """简单心跳检测"""
    return {"message": "pong"}

@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok"}

@app.get("/")
def home():
    """首页"""
    return {
        "message": "My Custom Connector is running successfully!",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

# ---------- 示例业务接口 ----------
@app.post("/hello")
def say_hello(req: HelloRequest):
    """问候接口"""
    return {"message": f"Hello, {req.name}! Your connector works perfectly."}

# ---------- ChatGPT 兼容性补丁 ----------
@app.get("/openapi.json")
def get_openapi():
    """
    ChatGPT 会通过 GET 请求读取 OpenAPI schema
    """
    return app.openapi()

@app.post("/openapi.json")
async def post_openapi(request: Request):
    """
    ChatGPT MCP 验证时会对 /openapi.json 发起 POST 请求
    这里返回与 GET 相同的内容即可，避免 405 错误
    """
    return JSONResponse(app.openapi())
