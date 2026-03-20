# 📌 SRPHS – Sistema de Recomendación para Hábitos Saludables

## 👤 Developers
- **Juan Pablo Caballero** - *FullStack | Cloud | AI | Database*
- **Robinson Nuñez** - *Collaborator & Frontend Partner*

## 📑 Contenido
1. [Descripción del Proyecto](#-descripción-del-proyecto)
2. [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
3. [Documentación API](#-api-endpoints)
4. [Inteligencia Artificial y XAI](#-inteligencia-artificial-y-xai)
5. [Tecnologías](#-tecnologías)
6. [Estrategia de Branches](#-branch-strategy--structure)
7. [Getting Started](#-getting-started)
8. [Variables de Envornno](#-variables-de-entorno)

---

## 📝 Descripción del Proyecto

El **SRPHS** es una plataforma inteligente diseñada para la prevención de riesgos metabólicos y obesidad. Utiliza modelos de **Machine Learning** para analizar hábitos de vida y proporciona recomendaciones personalizadas.

---

## 🏢 Arquitectura del Proyecto

El backend está construido con **FastAPI** siguiendo una estructura modular que separa los modelos de datos de la lógica de negocio:

- **🧠 Models:** Definición de documentos para MongoDB usando **Beanie ODM** (User y HealthRecord).
- **⚙️ Services/ML:** Carga de modelos `.joblib` y procesamiento de datos con Pandas/NumPy.
- **🔌 API Routes:** Endpoints optimizados para registro, login, predicción y analítica.
- **💾 Database:** Persistencia asíncrona en **MongoDB Atlas**.

---

## 📂 Estructura del Proyecto
```
:📂 SRPHS_BACKEND
┣ :📂 src/
┃ ┣ :📂 com/srphs/app/
┃ ┃ ┣ 📄 main.py                # Punto de entrada de FastAPI
┃ ┃ ┣ :📂 models/               # Modelos de Beanie (User, Record)
┃ ┃ ┣ :📂 schemas/              # Validaciones de Pydantic
┃ ┃ ┣ :📂 database/             # Configuración de MongoDB (Repository)
┃ ┃ ┗ :📂 ml_models/            # Archivos .joblib (RF Model)
┣ 📄 .env                       # Variables críticas 
┗ 📄 README.md
```

---

## 📡 API Endpoints

La documentación interactiva se encuentra disponible vía **Swagger UI**:  
🔗 `http://127.0.0.1:8000/docs`

### Principales Rutas:
- `POST /register`: Registro de nuevos usuarios con hashing de seguridad.
- `POST /login`: Validación de credenciales.
- `POST /predict`: Generación de diagnóstico IA y guardado en historial.
- `GET /history/{email}`: Recuperación de la evolución del usuario.
- `GET /analytics/{email}`: Resumen estadístico de factores críticos.

---

## 🤖 Inteligencia Artificial y XAI

El sistema no solo predice, sino que explica sus decisiones:
- **Modelo:** Random Forest Classifier optimizado.
- **XAI (SHAP):** Implementación de *Shapley Additive Explanations* para identificar qué hábitos específicos (CH2O, FAF, etc.) impactan más en el usuario, permitiendo generar recomendaciones humanas y coherente.

---

## 🧰 Tecnologías

### Backend & AI
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-0058ED?style=for-the-badge&logo=fastapi&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

### Database & Security
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Bcrypt](https://img.shields.io/badge/Bcrypt-Security-blue?style=for-the-badge)

### Design & Documentation
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)
![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white)
![Render](https://img.shields.io/badge/render-%23F24E.svg?style=for-the-badge&logo=render&logoColor=white)

---

## ⚡ Getting Started

### 1️ Preparar el Entorno (Windows)

```bash
# Crear entorno virtual

python -m venv venv

# Activar entorno virtual

.\venv\Scripts\activate

# Instalar dependencias necesarias

pip install fastapi uvicorn pandas numpy scikit-learn shap joblib bcrypt motor beanie python-dotenv

# Ejecuta un servidor web que pone en línea el API de FastAPI y se reinicia automáticamente cada vez que se guarda un cambio en el código.

uvicorn src.com.srphs.app.main:app --reload

# Instala el combo para manejar seguridad de contraseñas, conexión asíncrona a MongoDB, el mapeo de objetos (ODM) y validación de correos.

pip install passlib[bcrypt] motor beanie email-validator

# Instala la librería de Inteligencia Artificial Explicable (XAI) que permite entender qué variables afectan más a la predicción.

pip install shap

# Instala las herramientas necesarias para que Python se comunique con MongoDB de forma asíncrona.

pip install motor beanie

# Instala el algoritmo de cifrado para encriptar las contraseñas de los usuarios de forma segura antes de guardarlas.

pip install bcrypt

# Instala la librería que permite leer las variables secretas desde el archivo .env.
pip install python-dotenv