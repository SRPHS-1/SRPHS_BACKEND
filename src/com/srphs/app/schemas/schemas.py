from pydantic import BaseModel
from typing import Literal

class PredictionInput(BaseModel):
    # Atributos biológicos y demográficos
    Gender: str                         # 'Male' o 'Female'
    Age: int                            # Edad del usuario
    Height: float                       # Altura en metros (ej. 1.75)
    Weight: float                       # Peso en kilogramos (ej. 80.0)
    
    # Antecedentes y hábitos alimenticios
    family_history_with_overweight: str # Historial familiar con sobrepeso ('yes' o 'no')
    FAVC: str                           # Consumo frecuente de alimentos calóricos ('yes' o 'no')
    FCVC: int                           # Consumo de vegetales (1: Nunca, 2: A veces, 3: Siempre)
    NCP: int                            # Número de comidas principales al día (1 a 4)
    CAEC: str                           # Consumo de alimentos entre comidas ('Sometimes', 'Frequently', 'Always', 'no')
    
    # Estilo de vida y salud
    SMOKE: str                          # Si el usuario fuma ('yes' o 'no')
    CH2O: int                           # Consumo diario de agua (1: <1L, 2: 1-2L, 3: >2L)
    SCC: str                            # Monitoreo de consumo de calorías ('yes' o 'no')
    FAF: int                            # Frecuencia de actividad física (0: nada, 1: 1-2 días, 2: 2-4 días, 3: 4-5 días)
    TUE: int                            # Tiempo de uso de dispositivos tecnológicos (0: 0-2h, 1: 3-5h, 2: >5h)
    
    # Consumo de sustancias y transporte
    CALC: str                           # Consumo de alcohol ('Sometimes', 'Frequently', 'Always', 'no')
    MTRANS: str                         # Medio de transporte principal ('Public_Transportation', 'Walking', 'Automobile', 'Motorbike', 'Bike')
    
    # Objetivo del usuario 
    goal: Literal["perder", "mantener", "ganar"] = "mantener"