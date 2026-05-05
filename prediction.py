import joblib
import pandas as pd

model = joblib.load("backend/ml/fitpic_model.pkl")

def predict_outfit(color, style, season):
    input_data = pd.DataFrame([{
        "color": color,
        "style": style,
        "season": season
    }])
    
    prediction = model.predict(input_data)[0]
    confidence = model.predict_proba(input_data)[0][1]
    
    return {
        "liked": int(prediction),
        "confidence": float(confidence)
    }
