import os
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
            raise ValueError("No GEMINI_API_KEY found in environment variables")

        self.client = Client(api_key=api_key)

        try:
            available_models = [m.name for m in self.client.models.list()]

            if "models/gemini-2.5-flash" in available_models:
                self.model_id = "models/gemini-2.5-flash"
            elif "models/gemini-2.0-flash" in available_models:
                self.model_id = "models/gemini-2.0-flash"
            elif "models/gemini-1.5-flash" in available_models:
                self.model_id = "models/gemini-1.5-flash"
            else:
                self.model_id = next(
                    (m for m in available_models if "flash" in m),
                    "models/gemini-1.5-flash",
                )
            print(f"DEBUG - Usando modelo: {self.model_id}")

        except Exception as e:
            print(f"DEBUG - No se pudo listar modelos: {e}")
            self.model_id = "models/gemini-1.5-flash"

    def generate_personalized_recommendations(
        self,
        prediction_label: str,
        top_shap_features: list,
        goal: str = "mantener",
    ) -> str:
        """
        Genera recomendaciones combinando la predicción, los factores SHAP
        y el objetivo personal del usuario (perder / mantener / ganar).
        """
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
        
        Teniendo en cuenta tanto el diagnóstico como el objetivo personal:
        
        1. Explica brevemente y en tono motivador por qué estos factores afectan su salud.
        2. Genera exactamente 3 recomendaciones de acción concretas que:
        - Ataquen directamente los factores identificados.
        - Estén alineadas con el objetivo de '{goal_text}'.
        - Sean específicas, realizables y sin lenguaje médico excesivo.
        
        RESPONDE EXCLUSIVAMENTE EN FORMATO JSON con esta estructura exacta:
        {{
            "explicacion_contextual": "...",
            "acciones": ["Recomendación 1", "Recomendación 2", "Recomendación 3"],
            "tono": "motivacional"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            return response.text.strip().replace("```json", "").replace("```", "")

        except Exception as e:
            return f'{{"error": "Error en el servicio de IA: {str(e)}"}}'