import joblib
import pandas as pd
import shap
import os
import json
from .gemini_service import GeminiRecommendationService

class AIService:
    def __init__(self, model_path, encoder_path):
        self.model = joblib.load(model_path)
        self.encoders = joblib.load(encoder_path)
        self.explainer = shap.TreeExplainer(self.model)
        
        self.gemini = GeminiRecommendationService()
        
        self.feature_names_friendly = {
            "Age": "Edad",
            "Gender": "Género",
            "Height": "Altura",
            "Weight": "Peso",
            "family_history_with_overweight": "Antecedentes familiares de sobrepeso",
            "FAVC": "Consumo frecuente de alimentos hipercalóricos",
            "FCVC": "Consumo de verduras en las comidas",
            "NCP": "Número de comidas principales",
            "CAEC": "Consumo de alimentos entre comidas",
            "SMOKE": "Hábito de fumar",
            "CH2O": "Consumo diario de agua",
            "SCC": "Monitoreo de calorías consumidas",
            "FAF": "Frecuencia de actividad física",
            "TUE": "Tiempo de uso de dispositivos tecnológicos (sedentarismo digital)",
            "CALC": "Consumo de alcohol",
            "MTRANS": "Medio de transporte principal"
        }

    def analyze_health(self, input_dict: dict):
        # 1. Preparar los datos para el modelo
        input_df = pd.DataFrame([input_dict])
        
        for col, le in self.encoders.items():
            if col in input_df.columns and col != 'NObeyesdad':
                input_df[col] = le.transform(input_df[col])
        
        # 2. Realizar predicción
        prediction_numeric = int(self.model.predict(input_df)[0])
        result_label = self.encoders['NObeyesdad'].inverse_transform([prediction_numeric])[0]
        
        # 3. Análisis de explicabilidad (SHAP)
        shap_values = self.explainer.shap_values(input_df)
        
        if isinstance(shap_values, list):
            current_shap = shap_values[prediction_numeric][0]
        else:
            current_shap = shap_values[0, :, prediction_numeric] if len(shap_values.shape) == 3 else shap_values[0]

        # 4. Identificar factores con mayor impacto negativo
        feature_importance = dict(zip(input_df.columns, current_shap))
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        top_factors = [
            {
                "feature_name": self.feature_names_friendly.get(k, k), 
                "is_positive_influence": True
            } 
            for k, v in sorted_features[:3] if v > 0
        ]

        # 5. Generar recomendaciones inteligentes con Gemini
        smart_recs_raw = self.gemini.generate_personalized_recommendations(result_label, top_factors)
        try:
            clean_text = smart_recs_raw.strip().replace("```json", "").replace("```", "")
            smart_recs_dict = json.loads(clean_text)
            
            lista_para_db = smart_recs_dict.get("acciones", ["Seguir indicaciones médicas"])
            
        except Exception:
            lista_para_db = ["Mantener hábitos saludables", "Consultar a su médico", "Seguir monitoreando su peso"]

        return result_label, lista_para_db, feature_importance