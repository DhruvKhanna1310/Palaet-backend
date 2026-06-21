from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from routers import inventory, recommend, analytics

load_dotenv()

app = FastAPI(
    title="Palate API",
    description="AI-powered wine discovery backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory.router)
app.include_router(recommend.router)
app.include_router(analytics.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "Palate API", "version": "1.0.0"}
    