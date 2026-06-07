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
        self.model_id = "gemini-1.5-flash"
        
        print(f"DEBUG - Inicializando servicio con modelo: {self.model_id}")
        
        # DEBUG: Listar modelos disponibles para ver exactamente cómo los llama Google
        try:
            print("DEBUG - Intentando listar modelos para verificar nombres:")
            available = self.client.models.list()
            for m in available:
                print(f"DEBUG - Modelo encontrado en lista: {m.name}")
        except Exception as e:
            print(f"DEBUG - No se pudo listar modelos (posible restricción regional): {e}")

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

        print(f"DEBUG - Enviando prompt al modelo: {self.model_id}")
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
            )
            
            text = response.text.strip()
            clean_text = text.replace("```json", "").replace("```", "").strip()
            print(f"DEBUG - Respuesta recibida de API: {clean_text[:100]}...") # Imprimir parte de la respuesta
            
            return clean_text

        except Exception as e:
            print(f"DEBUG - ! ERROR CRÍTICO AL GENERAR CONTENIDO !")
            print(f"DEBUG - Detalles del error: {str(e)}")
            
            error_json = {
                "explicacion_contextual": "Hubo un error técnico al contactar con la IA.",
                "acciones": ["Reintentar la solicitud", "Verificar logs de Render", "Contactar a soporte"],
                "tono": "informativo"
            }
            return json.dumps(error_json)
