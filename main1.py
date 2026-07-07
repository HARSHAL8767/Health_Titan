from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import engine, Base
import models  # registers all models so create_all works
from raouth import router

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title       = "Health Titan API",
    description = "Backend for Health Titan — Personal Health & Diet Tracking Platform",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # restrict to your frontend URL in production
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def root():
    return {"status": "Health Titan API is running ✅"}