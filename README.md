# My Custom Connector

A simple FastAPI backend designed for integration with ChatGPT Connectors.

## Local Run

```bash
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Visit:

- http://localhost:8000/docs
- http://localhost:8000/openapi.json

## Deploy to Render

1. Push this repository to GitHub.
2. Go to https://render.com
3. Click "New → Web Service"
4. Choose your GitHub repository.
5. Use the following commands:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port 10000`
6. After deployment, verify:
   - `/ping` returns `{"message":"pong"}`
   - `/health` returns `{"status":"ok"}`
   - `/openapi.json` is accessible for ChatGPT Connector.
