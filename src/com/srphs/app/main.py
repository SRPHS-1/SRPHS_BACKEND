import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .schemas.schemas import PredictionInput
from .models.user import User
from .models.record import HealthRecord
from .database.repository import init_db

from .services.ai_service import AIService
from .services.auth_service import AuthService
from .services.google_auth_service import GoogleAuthService

load_dotenv()

app = FastAPI(
    title="SRPHS - Sistema Recomendación Para Hábitos Saludables",
    description="Backend inteligente con FastAPI, Random Forest, SHAP y Gemini AI",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "obesity_rf_model.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoders.joblib")

if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
    from .services.model_service import train_model
    train_model()
    
ai_service     = AIService(MODEL_PATH, ENCODER_PATH)
auth_service   = AuthService()
google_service = GoogleAuthService()

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


# Schemas auxiliares 
class GoogleAuthRequest(BaseModel):
    credential: str   # JWT token enviado por Google al frontend


# Startup para inicializar la conexión a la base de datos
@app.on_event("startup")
async def start_db():
    await init_db()


# Auth local para registro y login con email/contraseña 
@app.post("/register")
async def register(user_data: User):
    existing = await User.find_one(User.email == user_data.email)
    if existing:
        return {"status": "error", "message": "El correo ya está registrado"}
    user_data.password = auth_service.hash_password(user_data.password)
    user_data.auth_provider = "local"
    await user_data.insert()
    return {"status": "success", "message": "Usuario registrado exitosamente"}


@app.post("/login")
async def login(email: str, password: str):
    user = await User.find_one(User.email == email)
    if not user:
        return {"status": "error", "message": "Credenciales inválidas"}
    if user.auth_provider == "google":
        return {"status": "error", "message": "Esta cuenta usa Google. Inicia sesión con Google."}
    if not auth_service.verify_password(password, user.password):
        return {"status": "error", "message": "Credenciales inválidas"}
    return {
        "status":   "success",
        "message":  "Login exitoso",
        "user":     user.username,
        "avatar":   user.avatar_url or "",
    }


# Auth Google que combina registro y login en un solo endpoint para simplificar la integración con Google One Tap en el frontend
@app.post("/auth/google/register")
async def google_register(body: GoogleAuthRequest):
    """
    Registra un usuario nuevo con Google.
    Si el email ya existe retorna error — debe hacer login.
    """
    try:
        info = google_service.verify_token(body.credential)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")

    existing = await User.find_one(User.email == info["email"])
    if existing:
        return {"status": "error", "message": "Ya tienes una cuenta. Inicia sesión."}

    new_user = User(
        username=info["name"] or info["email"].split("@")[0],
        email=info["email"],
        google_id=info["google_id"],
        auth_provider="google",
        avatar_url=info["avatar_url"],
    )
    await new_user.insert()

    return {
        "status":   "success",
        "message":  "Cuenta creada con Google",
        "user":     new_user.username,
        "avatar":   new_user.avatar_url or "",
    }


@app.post("/auth/google/login")
async def google_login(body: GoogleAuthRequest):
    """
    Login con Google.
    Si el email no existe retorna error — debe registrarse primero.
    """
    try:
        info = google_service.verify_token(body.credential)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")

    user = await User.find_one(User.email == info["email"])
    if not user:
        return {"status": "error", "message": "No tienes cuenta. Regístrate primero con Google."}

    # Si existe pero se registró con contraseña
    if user.auth_provider == "local":
        return {"status": "error", "message": "Esta cuenta usa contraseña. Inicia sesión con tu correo."}

    # Actualizar avatar por si cambió en Google
    if user.avatar_url != info["avatar_url"]:
        user.avatar_url = info["avatar_url"]
        await user.save()

    return {
        "status":   "success",
        "message":  "Login exitoso con Google",
        "user":     user.username,
        "avatar":   user.avatar_url or "",
    }


# Predicción y recomendaciones inteligentes
@app.post("/predict")
async def predict(data: PredictionInput, user_email: str):
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
        "status":       "success",
        "prediction":   label,
        "recommendations": smart_tips,
        "goal":         goal,
        "ai_analysis":  "Análisis generado por Gemini Flash + SHAP",
        "shap_scores":  {k: round(float(v), 4) for k, v in importance.items()},
    }


# Historial y analíticas 
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
            "estado_actual":      records[0].prediction,
            "objetivo_actual":    records[0].goal or "mantener",
            "ultimo_consejo":     (
                records[0].top_recommendations[0]
                if records[0].top_recommendations else "N/A"
            ),
        },
    }