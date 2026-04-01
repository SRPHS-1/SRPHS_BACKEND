# 🌿 SRPHS — Sistema de Recomendación para Hábitos Saludables

> Backend inteligente con FastAPI, Random Forest, SHAP y Gemini AI

[![Python](https://img.shields.io/badge/Python-3.12-3670A0?style=flat-square&logo=python&logoColor=ffdd54)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://srphs-backend.onrender.com)

**API en producción:** https://srphs-backend.onrender.com  
**Documentación interactiva:** https://srphs-backend.onrender.com/docs

---

## 👥 Desarrolladores

| Nombre | Rol |
|---|---|
| **Juan Pablo Caballero** | FullStack · Cloud · AI · Database |
| **Robinson Núñez** | Collaborator & Frontend Partner · AI · Database  |

---

## 📑 Contenido

1. [Descripción](#-descripción)
2. [Arquitectura](#-arquitectura)
3. [Endpoints API](#-endpoints-api)
4. [Inteligencia Artificial](#-inteligencia-artificial)
5. [Stack tecnológico](#-stack-tecnológico)
6. [Instalación local](#-instalación-local)
7. [Variables de entorno](#-variables-de-entorno)
8. [Estructura del proyecto](#-estructura-del-proyecto)

---

## 📝 Descripción

SRPHS es una plataforma inteligente para la prevención de riesgos metabólicos y obesidad. Analiza hábitos de vida del usuario mediante **Machine Learning** y genera recomendaciones personalizadas usando **Gemini AI**, explicando el razonamiento con **SHAP (XAI)**.

**Flujo principal:**
1. El usuario ingresa sus datos (edad, peso, altura, hábitos alimenticios, actividad física, etc.)
2. Un modelo **Random Forest** predice su nivel de riesgo de obesidad
3. **SHAP** identifica los factores que más influyen en el resultado
4. **Gemini Flash** genera recomendaciones concretas y personalizadas según el objetivo del usuario (perder / mantener / ganar peso)
5. El historial queda guardado en **MongoDB Atlas** para seguimiento evolutivo

---

## 📄 Documentación del proyecto

| Documento | Descripción |
|---|---|
| [📘 Informe técnico](docs/Proyecto_SRPHS_CaballeroJuan_NuñezRobinson.pdf) | Sistema de recomendación personalizada de hábitos saludables — Documento académico del proyecto de IA |

---


## 🏗️ Arquitectura

```
SRPHS_BACKEND/
└──docs
    ├──Proyecto_SRPHS_CaballeroJuan_NuñezRobinson.pdf
└── src/com/srphs/app/
    ├── main.py               # Punto de entrada FastAPI + CORS + rutas
    ├── database/
    │   └── repository.py     # Inicialización Beanie + MongoDB
    ├── models/
    │   ├── user.py           # Documento User (Beanie)
    │   └── record.py         # Documento HealthRecord (Beanie)
    ├── schemas/
    │   └── schemas.py        # Validación de entrada (Pydantic)
    ├── services/
    │   ├── ai_service.py     # Random Forest + SHAP + Gemini
    │   ├── auth_service.py   # Hash y verificación de contraseñas (bcrypt)
    │   ├── gemini_service.py # Generación de recomendaciones con Gemini
    │   ├── google_auth_service.py  # Verificación de tokens OAuth2 Google
    │   └── model_service.py  # Entrenamiento del modelo (auto-train)
    └── data/
        └── obesity_data.csv  # Dataset de entrenamiento
```

---

## 📡 Endpoints API

### Autenticación local

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/register` | Registro con email y contraseña |
| `POST` | `/login` | Login con email y contraseña |

### Autenticación Google OAuth2

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/auth/google/register` | Registro con cuenta de Google |
| `POST` | `/auth/google/login` | Login con cuenta de Google |

### Predicción y datos

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/predict` | Genera predicción + recomendaciones IA |
| `GET` | `/history/{email}` | Historial de evaluaciones del usuario |
| `GET` | `/analytics/{email}` | Resumen estadístico del usuario |

---

## 🤖 Inteligencia Artificial

### Modelo predictivo
- **Algoritmo:** Random Forest Classifier (`scikit-learn`)
- **Dataset:** 2.111 registros con 17 variables de hábitos de vida
- **Precisión:** ~95.5% en conjunto de prueba
- **Auto-entrenamiento:** Si los archivos `.joblib` no existen al iniciar, el modelo se entrena automáticamente

### Variables de entrada
El modelo analiza: género, edad, altura, peso, antecedentes familiares, consumo de alimentos hipercalóricos, frecuencia de vegetales, número de comidas, snacks entre comidas, tabaquismo, consumo de agua, monitoreo de calorías, actividad física, tiempo en pantallas, alcohol y medio de transporte.

### Explicabilidad (SHAP)
Tras la predicción, **SHAP TreeExplainer** identifica los 3 factores con mayor impacto en el resultado, que luego se pasan a Gemini para generar recomendaciones dirigidas.

### Recomendaciones con Gemini
`gemini-2.5-flash` (con fallback a versiones anteriores) recibe el diagnóstico, los factores SHAP y el **objetivo personal del usuario** (perder / mantener / ganar peso) para generar 3 recomendaciones concretas y motivadoras en formato JSON.

---

## 🧰 Stack tecnológico

| Capa | Tecnología |
|---|---|
| Framework | FastAPI 0.135 |
| ML | scikit-learn, SHAP, pandas |
| IA generativa | Google Gemini Flash (google-genai) |
| Base de datos | MongoDB Atlas + Motor + Beanie 1.30 |
| Auth | bcrypt + Google OAuth2 |
| Deploy | Render (free tier) |

---

## ⚡ Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/SRPHS-1/SRPHS_BACKEND.git
cd SRPHS_BACKEND

# 2. Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Levantar el servidor
uvicorn src.com.srphs.app.main:app --reload
```

La API estará disponible en `http://localhost:8000` y la documentación en `http://localhost:8000/docs`.

> **Nota:** El modelo se entrena automáticamente al primer arranque si no existe el archivo `.joblib`. Esto puede tomar ~30 segundos.

---

## 🔐 Variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/SRPHS_DB
GEMINI_API_KEY=tu_gemini_api_key
GOOGLE_CLIENT_ID=tu_google_oauth_client_id
PORT=8000
PYTHON_VERSION=3.12
```

| Variable | Descripción |
|---|---|
| `MONGO_URI` | Cadena de conexión a MongoDB Atlas |
| `GEMINI_API_KEY` | API key de Google AI Studio |
| `GOOGLE_CLIENT_ID` | Client ID de Google Cloud Console (OAuth2) |
| `PORT` | Puerto del servidor (Render lo asigna automáticamente) |

---

## 📌 Notas de despliegue

- El backend está desplegado en **Render** (free tier) — puede tardar ~50 segundos en responder tras inactividad (cold start).
- Los archivos `.joblib` del modelo **no se versionan** en Git. Se generan automáticamente en el primer arranque mediante `model_service.py`.
- El CORS está configurado para aceptar requests desde `localhost:5173` y el dominio de Vercel del frontend.
