import os
import joblib
import numpy as np
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from utils.database import db

FRUIT_MAP     = {"bright": 1.0, "fresh": 3.0, "dark": 5.0, "stone": 4.0, "any": 3.0}
TEXTURE_MAP   = {"light": 2.0, "medium": 5.0, "bold": 9.0, "any": 5.0}
SWEETNESS_MAP = {"dry": 1.0, "off-dry": 4.0, "sweet": 8.0, "any": 3.0}
OCCASION_MAP  = {"solo": 3.0, "casual": 5.0, "intimate": 7.0, "formal": 8.0, "any": 5.0}
BUDGET_MAP    = {"low": 15.0, "mid": 37.5, "high": 70.0, "any": 37.5}

MODEL_PATH   = "models/knn_model.pkl"
MIN_SESSIONS = 50

def session_to_vector(session):
    fruit     = FRUIT_MAP.get(session.get("ans_fruit", "any"), 3.0)
    texture   = TEXTURE_MAP.get(session.get("ans_texture", "any"), 5.0)
    sweetness = SWEETNESS_MAP.get(session.get("ans_sweetness", "any"), 3.0)
    occasion  = OCCASION_MAP.get(session.get("ans_occasion", "any"), 5.0)
    budget    = BUDGET_MAP.get(session.get("ans_budget", "any"), 37.5)
    try:
        ts = session.get("timestamp", "")
        hour = datetime.fromisoformat(ts.replace("Z", "+00:00")).hour if ts else 18
    except:
        hour = 18
    try:
        ts = session.get("timestamp", "")
        dow = datetime.fromisoformat(ts.replace("Z", "+00:00")).weekday() if ts else 5
    except:
        dow = 5
    duration = session.get("duration_seconds", 60) or 60
    return [fruit, texture, sweetness, occasion, budget, hour/23.0, dow/6.0, min(duration,120)/120.0]

def train_model(store_id=None):
    print("Training KNN model (8 dimensions)...")
    query = db.table("sessions").select("ans_fruit,ans_texture,ans_sweetness,ans_occasion,ans_budget,timestamp,duration_seconds,purchased_id").not_.is_("purchased_id", "null")
    if store_id:
        query = query.eq("store_id", store_id)
    result = query.execute()
    sessions = result.data
    if len(sessions) < MIN_SESSIONS:
        print(f"Only {len(sessions)} sessions — need {MIN_SESSIONS} minimum.")
        return None
    print(f"Found {len(sessions)} purchased sessions")
    X, y = [], []
    for s in sessions:
        if not s.get("purchased_id"):
            continue
        X.append(session_to_vector(s))
        y.append(s["purchased_id"])
    X = np.array(X)
    y = np.array(y)
    print(f"Feature matrix: {X.shape} — Unique wines: {len(set(y))}")
    k = max(3, min(20, int(np.sqrt(len(X)))))
    print(f"Training KNN k={k}...")
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=k, metric="cosine", weights="distance", algorithm="brute"))
    ])
    model.fit(X, y)
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return model

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def get_knn_scores(session, candidate_wine_ids):
    model = load_model()
    if model is None:
        return {}
    try:
        X = np.array([session_to_vector(session)])
        probs = model.predict_proba(X)[0]
        classes = model.classes_
        return {wid: float(p) for wid, p in zip(classes, probs) if wid in candidate_wine_ids}
    except Exception as e:
        print(f"KNN error: {e}")
        return {}

def get_session_count(store_id=None):
    query = db.table("sessions").select("id", count="exact").not_.is_("purchased_id", "null")
    if store_id:
        query = query.eq("store_id", store_id)
    result = query.execute()
    return result.count or 0

def get_blend_weight(session_count):
    if session_count < 50:   return 0.0
    if session_count < 200:  return 0.2
    if session_count < 500:  return 0.4
    if session_count < 1000: return 0.6
    if session_count < 2000: return 0.75
    return 0.85
