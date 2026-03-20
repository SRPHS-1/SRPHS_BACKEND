import joblib
import pandas as pd
import shap
import numpy as np
import os
import bcrypt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .schemas.schemas import PredictionInput
from .models.user import User
from .models.record import HealthRecord
from .database.repository import init_db

load_dotenv()

app = FastAPI(title="SRPHS - Sistema Recomendación Para Hábitos Saludables")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "obesity_rf_model.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "models", "label_encoders.joblib")

MODEL = joblib.load(MODEL_PATH)
ENCODERS = joblib.load(ENCODER_PATH)
explainer = shap.TreeExplainer(MODEL)

MESSAGES = {
    "CH2O": "💧 Tu nivel de hidratación es el factor que más está elevando tu riesgo metabólico.",
    "FAF": "🏃‍♂️ La falta de actividad física constante es tu principal debilidad actual.",
    "FAVC": "🍔 El consumo frecuente de alimentos calóricos está pesando mucho en tu diagnóstico.",
    "FCVC": "🥦 La baja ingesta de vegetales está afectando negativamente tu metabolismo.",
    "TUE": "📱 El sedentarismo digital y tiempo frente a pantallas es un factor crítico para ti.",
    "Age": "🎂 Tu edad actual requiere un ajuste metabólico y nutricional específico.",
    "family_history_with_overweight": "🧬 Tus antecedentes familiares tienen un peso importante en tu perfil de riesgo.",
    "MTRANS": "🚗 Tu medio de transporte actual está fomentando un estilo de vida sedentario.",
    "CAEC": "🍪 El hábito de consumir alimentos entre comidas está impactando tu peso.",
    "CALC": "🍷 El consumo de alcohol está influyendo en tu balance calórico diario."
}

@app.on_event("startup")
async def start_db():
    await init_db()

@app.post("/register")
async def register(user_data: User):
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        return {"status": "error", "message": "El correo ya está registrado"}
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(user_data.password.encode('utf-8'), salt)
    user_data.password = hashed.decode('utf-8')
    
    await user_data.insert()
    return {"status": "success", "message": "Usuario registrado exitosamente"}

@app.post("/login")
async def login(email: str, password: str):
    user = await User.find_one(User.email == email)
    if not user:
        return {"status": "error", "message": "Usuario no encontrado"}
    
    is_valid = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
    if not is_valid:
        return {"status": "error", "message": "Credenciales inválidas"}
    
    return {"status": "success", "message": "Login exitoso", "user": user.username}

@app.post("/predict")
async def predict(data: PredictionInput, user_email: str):
    input_dict = data.model_dump()
    input_df = pd.DataFrame([input_dict])
    
    for col, le in ENCODERS.items():
        if col in input_df.columns and col != 'NObeyesdad':
            input_df[col] = le.transform(input_df[col])
    
    prediction_numeric = int(MODEL.predict(input_df)[0])
    result = ENCODERS['NObeyesdad'].inverse_transform([prediction_numeric])[0]
    
    shap_values = explainer.shap_values(input_df)

    if isinstance(shap_values, list):
        current_shap_importance = shap_values[prediction_numeric][0]
    else:
        current_shap_importance = shap_values[0, :, prediction_numeric] if len(shap_values.shape) == 3 else shap_values[0]

    feature_importance = dict(zip(input_df.columns, current_shap_importance))
    sorted_habits = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    
    tips = []
    for habit, weight in sorted_habits[:3]:
        if weight > 0:
            tips.append(MESSAGES.get(habit, f"⚠️ El factor {habit} influye en tu diagnóstico."))

    new_record = HealthRecord(
        user_email=user_email,
        prediction=result,
        weight=data.Weight,
        height=data.Height,
        top_recommendations=tips
    )
    await new_record.insert()

    return {
        "status": "success",
        "prediction": result,
        "ai_analysis": "Explicabilidad mediante valores de Shapley (XAI)",
        "top_recommendations": tips,
        "shap_scores": {k: round(float(v), 4) for k, v in feature_importance.items()}
    }

@app.get("/history/{email}")
async def get_history(email: str):
    history = await HealthRecord.find(HealthRecord.user_email == email).sort("-date").to_list()
    return {"status": "success", "data": history}

@app.get("/analytics/{email}")
async def get_analytics(email: str):
    records = await HealthRecord.find(HealthRecord.user_email == email).to_list()
    
    if not records:
        raise HTTPException(status_code=404, detail="No hay historial para este usuario")

    total_records = len(records)
    latest_prediction = records[0].prediction
    
    all_tips = [tip for r in records for tip in r.top_recommendations]
    most_common_issue = max(set(all_tips), key=all_tips.count) if all_tips else "Ninguno"

    return {
        "status": "success",
        "summary": {
            "total_evaluaciones": total_records,
            "estado_actual": latest_prediction,
            "factor_critico_frecuente": most_common_issue
        }
    }