from fastapi import APIRouter, HTTPException
from ..schemas.schemas import PredictionInput
from ..models.record import HealthRecord
from ..services.ai_service import AIService
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH   = os.path.join(BASE_DIR, "models", "obesity_rf_model.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoders.joblib")

if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
    from ..services.model_service import train_model
    train_model()

ai_service = AIService(MODEL_PATH, ENCODER_PATH)

@router.post("/predict")
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
        "status": "success", "prediction": label,
        "recommendations": smart_tips, "goal": goal,
        "ai_analysis": "Análisis generado por Gemini Flash + SHAP",
        "shap_scores": {k: round(float(v), 4) for k, v in importance.items()},
    }

@router.get("/history/{email}")
async def get_history(email: str):
    history = await HealthRecord.find(HealthRecord.user_email == email).sort("-date").to_list()
    return {"status": "success", "data": history}

@router.get("/analytics/{email}")
async def get_analytics(email: str):
    records = await HealthRecord.find(HealthRecord.user_email == email).sort("-date").to_list()
    if not records:
        raise HTTPException(status_code=404, detail="No hay historial para este usuario")
    return {
        "status": "success",
        "summary": {
            "total_evaluaciones": len(records),
            "estado_actual":   records[0].prediction,
            "objetivo_actual": records[0].goal or "mantener",
            "ultimo_consejo":  records[0].top_recommendations[0] if records[0].top_recommendations else "N/A",
        },
    }