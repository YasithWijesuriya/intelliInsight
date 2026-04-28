# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, os
from app.agents.base import BaseAgent

from app.config import settings
from app.database import test_connection, Base, engine
from app.routers import upload

app = FastAPI(
    title="IntelliInsight API",
    description="Multi-Agent AI Enterprise Intelligence Platform",
    version="1.0.0"
)

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(upload.router)

@app.on_event("startup")
async def startup_event():
    print("🚀 IntelliInsight starting...")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    # Create all DB tables automatically
    Base.metadata.create_all(bind=engine)
    db_ok = test_connection()
    print("✅ Database: OK" if db_ok else "❌ Database: FAILED")
    print("✅ IntelliInsight ready!")
    print("OPENAI KEY:", settings.OPENAI_API_KEY)

@app.get("/")
async def root():
    return {"message": "IntelliInsight API", "status": "running"}

@app.get("/health")
async def health():
    return {
        "api": "healthy",
        "database": "connected" if test_connection() else "disconnected"
    }
from langchain_core.messages import HumanMessage
from app.agents.test import TestAgent

from fastapi import Query

@app.get("/chat")
async def chat(query: str = Query(...)):
    agent = TestAgent("TestAgent")
    result = await agent.run(query)
    return result

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0",
                port=settings.API_PORT, reload=True)