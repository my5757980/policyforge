from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from app.db import create_tables
from app.routers import policies, audit, demo

app = FastAPI(title="PolicyForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(policies.router)
app.include_router(audit.router)
app.include_router(demo.router)


@app.on_event("startup")
def on_startup():
    try:
        create_tables()
    except Exception as e:
        print(f"DB startup warning: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "service": "PolicyForge API"}
