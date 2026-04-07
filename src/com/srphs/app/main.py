import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .database.repository import init_db
from .presenters.auth_presenter import router as auth_router
from .presenters.health_presenter import router as health_router

load_dotenv()

app = FastAPI(
    title="SRPHS - Sistema Recomendación Para Hábitos Saludables",
    description="Backend inteligente con FastAPI, Random Forest, SHAP y Gemini AI",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://srphs-frontend-9hwt65qw1-robinsonsteven232-7270s-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def start_db():
    await init_db()

app.include_router(auth_router)
app.include_router(health_router)