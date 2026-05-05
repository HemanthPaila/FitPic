import pandas as pd
from model import get_recommendations

USER_DATA_PATH = "backend/ml/user_preferences.csv"

def load_user_data():
    try:
        return pd.read_csv(USER_DATA_PATH)
    except:
        return pd.DataFrame(columns=["color", "style", "liked"])

def save_feedback(data):
    df = pd.DataFrame([data])
    df.to_csv(USER_DATA_PATH, mode="a", header=False, index=False)

def rerank_results(results, user_data):
    if user_data.empty:
        return results

    liked_colors = user_data[user_data["liked"] == 1]["color"].tolist()
    
    for item in results:
        if any(c.lower() in item["color"].lower() for c in liked_colors):
            item["match_score"] += 10

    return sorted(results, key=lambda x: x["match_score"], reverse=True)


def get_personalized_recommendations(style, occasion, gender, good_colors):
    results = get_recommendations(
        style=style,
        occasion=occasion,
        gender=gender,
        good_colors=good_colors
    )

    user_data = load_user_data()
    results = rerank_results(results, user_data)

    return results
