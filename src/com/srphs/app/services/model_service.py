import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

DATA_PATH = "src/com/srphs/data/obesity_data.csv"
MODEL_PATH = "src/com/srphs/models/obesity_rf_model.joblib"
ENCODER_PATH = "src/com/srphs/models/label_encoders.joblib"

def train_model():
    df = pd.read_csv(DATA_PATH)
    
    encoders = {}
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    X = df.drop('NObeyesdad', axis=1)
    y = df['NObeyesdad']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    if not os.path.exists('models'):
        os.makedirs('models')
        
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)
    
    accuracy = model.score(X_test, y_test)
    print(f"✅ Modelo entrenado con éxito. Precisión (Accuracy): {accuracy:.2%}")
    return accuracy


train_model()