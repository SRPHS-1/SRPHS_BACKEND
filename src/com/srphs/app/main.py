import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .schemas.schemas import PredictionInput
from .models.user import User
from .models.record import HealthRecord
from .database.repository import init_db

from .services.ai_service import AIService
from .services.auth_service import AuthService

load_dotenv()

app = FastAPI(
    title="SRPHS - Sistema Recomendación Para Hábitos Saludables",
    description="Backend inteligente con FastAPI, Random Forest, SHAP y Gemini AI",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "obesity_rf_model.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoders.joblib")

ai_service = AIService(MODEL_PATH, ENCODER_PATH)
auth_service = AuthService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def start_db():
    await init_db()


@app.post("/register")
async def register(user_data: User):
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        return {"status": "error", "message": "El correo ya está registrado"}
    user_data.password = auth_service.hash_password(user_data.password)
    await user_data.insert()
    return {"status": "success", "message": "Usuario registrado exitosamente"}


@app.post("/login")
async def login(email: str, password: str):
    user = await User.find_one(User.email == email)
    if not user or not auth_service.verify_password(password, user.password):
        return {"status": "error", "message": "Credenciales inválidas"}
    return {"status": "success", "message": "Login exitoso", "user": user.username}


@app.post("/predict")
async def predict(data: PredictionInput, user_email: str):
    """
    Predicción de obesidad + SHAP + recomendaciones Gemini personalizadas por objetivo.
    """
    # ai_service ahora devuelve 4 valores (incluye goal)
    label, smart_tips, importance, goal = ai_service.analyze_health(data.model_dump())

    new_record = HealthRecord(
        user_email=user_email,
        prediction=label,
        weight=data.Weight,
        height=data.Height,
        top_recommendations=smart_tips,
        goal=goal,
    )
    await new_record.insert()

    return {
        "status": "success",
        "prediction": label,
        "recommendations": smart_tips,
        "goal": goal,
        "ai_analysis": "Análisis generado por Gemini Flash + SHAP",
        "shap_scores": {k: round(float(v), 4) for k, v in importance.items()},
    }


@app.get("/history/{email}")
async def get_history(email: str):
    history = (
        await HealthRecord.find(HealthRecord.user_email == email)
        .sort("-date")
        .to_list()
    )
    return {"status": "success", "data": history}


@app.get("/analytics/{email}")
async def get_analytics(email: str):
    records = (
        await HealthRecord.find(HealthRecord.user_email == email)
        .sort("-date")
        .to_list()
    )
    if not records:
        raise HTTPException(status_code=404, detail="No hay historial para este usuario")

    return {
        "status": "success",
        "summary": {
            "total_evaluaciones": len(records),
            "estado_actual": records[0].prediction,
            "objetivo_actual": records[0].goal or "mantener",
            "ultimo_consejo": (
                records[0].top_recommendations[0]
                if records[0].top_recommendations
                else "N/A"
            ),
        },
    }