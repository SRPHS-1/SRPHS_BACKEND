import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR  = os.path.dirname(BASE_DIR)

DATA_PATH    = os.path.join(APP_DIR, "data",   "obesity_data.csv")
MODEL_PATH   = os.path.join(APP_DIR, "models", "obesity_rf_model.joblib")
ENCODER_PATH = os.path.join(APP_DIR, "models", "label_encoders.joblib")

def train_model():
    df = pd.read_csv(DATA_PATH)

    encoders = {}
    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    X = df.drop('NObeyesdad', axis=1)
    y = df['NObeyesdad']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)

    accuracy = model.score(X_test, y_test)
    print(f"✅ Modelo entrenado. Precisión: {accuracy:.2%}")
    return accuracy