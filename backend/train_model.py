import csv
import os
import numpy as np
import xgboost as xgb
from sentence_transformers import SentenceTransformer
import torch

def train_xgboost_router():
    dataset_path = "dataset.csv"
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found. Run generate_dataset.py first.")
        # We will train on a fallback minimal set so the hackathon demo doesn't crash
        X_text = [
            "Hello", "What is 2+2?", "Tell me a joke", "What is the capital of France?",
            "Write a Rust macro for zero-copy deserialization.", 
            "Explain the nuances of the Riemann Hypothesis.", 
            "Draft a 10-page legally binding contract."
        ]
        y = [0, 0, 0, 0, 1, 1, 1]
    else:
        X_text = []
        y = []
        with open(dataset_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader) # skip header
            for row in reader:
                if len(row) == 2:
                    X_text.append(row[0])
                    y.append(int(row[1]))

    print(f"Loaded {len(X_text)} prompts for training.")
    
    # AMD ROCm Optimization: Push SentenceTransformer to CUDA (ROCm) if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading all-MiniLM-L6-v2 on {device.upper()}...")
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    
    print("Embedding text to 384-dimensional dense vectors...")
    # This directly feeds the dense embeddings into XGBoost, dropping TF-IDF
    X_features = model.encode(X_text, convert_to_numpy=True)
    
    print("Training XGBoost Classifier on dense embeddings...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=150, 
        learning_rate=0.1, 
        max_depth=4,
        use_label_encoder=False,
        eval_metric='logloss',
        tree_method='hist' # Highly optimized tree method
    )
    xgb_model.fit(X_features, y)
    
    print("Saving model...")
    xgb_model.save_model("xgboost_router.json")
    print("Training complete! XGBoost model saved to xgboost_router.json")
    print("(Note: tfidf_vectorizer.pkl is no longer needed and has been removed from the architecture.)")

if __name__ == "__main__":
    train_xgboost_router()
