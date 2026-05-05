import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
import joblib

# Load real user data
data = pd.read_csv("backend/ml/user_data.csv")

X = data[["color", "style", "season"]]
y = data["liked"]

model = Pipeline([
    ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ("classifier", LogisticRegression())
])

model.fit(X, y)

joblib.dump(model, "backend/ml/fitpic_model.pkl")

print("Model retrained!")
