import os
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()

class GeminiRecommendationService:
    def __init__(self):
        # 1. Configuración de la API Key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("No GEMINI_API_KEY found in environment variables")
        
        self.client = Client(api_key=api_key)
        
        try:
            available_models = [m.name for m in self.client.models.list()]
            
            if 'models/gemini-2.5-flash' in available_models:
                self.model_id = 'models/gemini-2.5-flash'
            elif 'models/gemini-2.0-flash' in available_models:
                self.model_id = 'models/gemini-2.0-flash'
            elif 'models/gemini-1.5-flash' in available_models:
                self.model_id = 'models/gemini-1.5-flash'
            else:
                self.model_id = next((m for m in available_models if 'flash' in m), 'models/gemini-1.5-flash')
            
            print(f"DEBUG - Usando el modelo detectado: {self.model_id}")
            
        except Exception as e:
            print(f"DEBUG - No se pudo listar modelos: {str(e)}")
            self.model_id = "models/gemini-1.5-flash" 

    def generate_personalized_recommendations(self, prediction_label, top_shap_features):
        """
        Genera recomendaciones inteligentes combinando la predicción y los factores clave de SHAP.
        """
        factors_text = ", ".join([
            f"'{f['feature_name']}' ({'factor de riesgo' if f['is_positive_influence'] else 'factor protector'})" 
            for f in top_shap_features
        ])
        
        prompt = f"""
        Actúa como un experto en nutrición y medicina preventiva para el proyecto SRPHS.
        Un paciente ha recibido un diagnóstico de: '{prediction_label}'.

        El análisis SHAP indica que los factores que más influyeron son: {factors_text}.

        Basado en esta información:
        1. Explica brevemente y en tono motivador por qué estos factores afectan su salud.
        2. Genera 3 recomendaciones de acción concretas que ataquen directamente esos factores.
        3. No uses un lenguaje excesivamente médico.

        RESPONDE EXCLUSIVAMENTE EN FORMATO JSON con esta estructura:
        {{
          "explicacion_contextual": "...",
          "acciones": ["Recomendación 1", "Recomendación 2", "Recomendación 3"],
          "tono": "motivacional/preventivo"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            text_response = response.text.strip().replace("```json", "").replace("```", "")
            return text_response
            
        except Exception as e:
            return f"{{\"error\": \"Error en el servicio de IA: {str(e)}\"}}"