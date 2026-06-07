import os
import json
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()

GOAL_LABELS = {
    "perder":   "pérdida de peso",
    "mantener": "mantenimiento del peso actual",
    "ganar":    "aumento de masa muscular y peso saludable",
}

class GeminiRecommendationService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No GEMINI_API_KEY found")
        
        self.client = Client(api_key=api_key)
        # Usamos el nombre limpio, sin prefijos, que es el estándar actual de la SDK
        self.model_id = "gemini-1.5-flash"

    def generate_personalized_recommendations(
        self,
        prediction_label: str,
        top_shap_features: list,
        goal: str = "mantener",
    ) -> str:
        
        goal_text = GOAL_LABELS.get(goal, "mantenimiento del peso actual")
        factors_text = ", ".join(
            [
                f"'{f['feature_name']}' "
                f"({'factor de riesgo' if f['is_positive_influence'] else 'factor protector'})"
                for f in top_shap_features
            ]
        )

        prompt = f"""
        Actúa como un experto en nutrición y medicina preventiva para el proyecto SRPHS.
        
        Un paciente ha recibido un diagnóstico de: '{prediction_label}'.
        Su objetivo personal declarado es: '{goal_text}'.
        Los factores que más influyeron según el análisis SHAP son: {factors_text}.
        
        1. Explica brevemente y en tono motivador por qué estos factores afectan su salud.
        2. Genera exactamente 3 recomendaciones de acción concretas.
        
        RESPONDE EXCLUSIVAMENTE EN FORMATO JSON:
        {{
            "explicacion_contextual": "...",
            "acciones": ["Rec 1", "Rec 2", "Rec 3"],
            "tono": "motivacional"
        }}
        """

        try:
            # Forzamos la llamada sin prefijos de 'models/'
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            text = response.text.strip()
            # Limpieza para asegurar formato JSON válido
            return text.replace("```json", "").replace("```", "").strip()

        except Exception as e:
            # Retornamos un JSON válido incluso en error para que el frontend no rompa
            error_json = {
                "explicacion_contextual": "No pudimos generar recomendaciones en este momento.",
                "acciones": ["Consultar con un profesional", "Mantener hábitos básicos", "Reintentar más tarde"],
                "tono": "informativo"
            }
            print(f"DEBUG - Error de IA: {str(e)}")
            return json.dumps(error_json)
