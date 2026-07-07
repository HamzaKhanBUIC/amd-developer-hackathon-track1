import json
import numpy as np
import xgboost as xgb
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Mock Chatbot Arena Data: 
# 0 = Easy (Llama 8B wins/ties) -> Route to Cheap Model
# 1 = Hard (Llama 70B wins exclusively) -> Route to Expensive Model
MOCK_DATA = [
    # Easy queries (Greeting, simple math, definitions)
    ("Hello, how are you?", 0),
    ("What is 2 + 2?", 0),
    ("Define the word 'computer'.", 0),
    ("Write a simple hello world in Python.", 0),
    ("What is the capital of France?", 0),
    ("Tell me a short joke.", 0),
    ("Translate 'Hello' to Spanish.", 0),
    ("What time is it?", 0),
    
    # Hard queries (Complex logic, deep reasoning, nuanced writing)
    ("Write a highly optimized Rust macro for zero-copy deserialization of a custom binary protocol.", 1),
    ("Explain the nuances of the Riemann Hypothesis and its implications for prime number distribution.", 1),
    ("Create a complete Next.js 14 architecture with server actions, optimistic updates, and React Query.", 1),
    ("Analyze the geopolitical ramifications of the 1973 oil crisis on modern renewable energy policies.", 1),
    ("Write a complex SQL query with multiple window functions, recursive CTEs, and lateral joins.", 1),
    ("Draft a 10-page legally binding contract for a joint venture between a US and EU corporation.", 1),
]

def train_xgboost_router():
    print("Preparing mock dataset...")
    X_text = [item[0] for item in MOCK_DATA]
    y = [item[1] for item in MOCK_DATA]
    
    print("Vectorizing text using TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=1000)
    X_features = vectorizer.fit_transform(X_text)
    
    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=100, 
        learning_rate=0.1, 
        max_depth=3,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    model.fit(X_features, y)
    
    print("Saving model and vectorizer...")
    model.save_model("xgboost_router.json")
    joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
    print("Training complete! Model saved to xgboost_router.json")

if __name__ == "__main__":
    train_xgboost_router()
