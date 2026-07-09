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
        # We will train on a comprehensive fallback set so the hackathon demo doesn't crash
        # 0 = Easy (Local), 1 = Hard (API)
        X_text = [
            # EASY (Label 0) - Greetings, NER, Sentiment, Simple Facts, Short Summaries
            "Hello there", "How are you doing today?", "Tell me a joke.", 
            "What is the capital of France?", "Who was the first president of the USA?",
            "Is the sentiment of this review positive or negative: 'I absolutely hated the food here.'",
            "Extract the names from this sentence: 'John and Mary bought a house in London.'",
            "What color is a ripe banana?", "Say hi.", "Good morning!",
            "Identify the organizations mentioned: 'Google and Microsoft reported earnings.'",
            "Classify this as happy or sad: 'This is the best day of my life.'",
            "Summarize this in one sentence: 'The cat slept all day on the warm windowsill.'",
            "What is the largest ocean on Earth?", "Name a mammal that can fly.",
            "Who wrote Romeo and Juliet?", "Extract locations: 'I traveled from Paris to Berlin.'",
            "Does this sound angry? 'I am so frustrated with this broken product!'",
            "Is 'Apple' a company or a fruit in this context: 'I ate an apple.'",
            "Translate 'Hello' to Spanish.", "What is 2+2?", "What is 5 plus 5?", # Simple math can go local
            "Tell me a short bedtime story.", "Write a haiku about nature.",
            "What year did the Titanic sink?", "What is the fastest land animal?",
            # HARD (Label 1) - Code, Advanced Math, Complex Logic, Factual Reasoning, Long Summaries
            "Write a Rust macro for zero-copy deserialization.",
            "Explain the nuances of the Riemann Hypothesis.",
            "Draft a 10-page legally binding contract for a corporate merger.",
            "What is the derivative of f(x) = x^2 * sin(x) / ln(x)?",
            "Implement a Red-Black Tree in C++ with deletion balancing.",
            "Write a multi-threaded web scraper in Go using goroutines.",
            "Calculate the eigenvectors of a 3x3 matrix.",
            "Solve the Navier-Stokes equation for a simplified 1D fluid flow.",
            "Create a full Next.js application with NextAuth and Prisma.",
            "Explain Quantum Entanglement and its implications for cryptography.",
            "Write a Python script to train a deep Convolutional Neural Network on CIFAR-10.",
            "Solve this logic puzzle: If A > B and B < C, is A > C?",
            "Design a microservices architecture for a high-traffic e-commerce site.",
            "What are the structural differences between an AVL tree and a B-Tree?",
            "Write a shell script that recursively finds all .txt files and compresses them.",
            "Prove that there are infinitely many prime numbers.",
            "Analyze the geopolitical implications of the 1973 oil crisis.",
            "Write an optimized SQL query with multiple window functions and CTEs.",
            "Explain the P vs NP problem in theoretical computer science.",
            "Create an assembly language program to reverse a string in memory.",
            "Detail the biochemical pathways of cellular respiration."
        ]
        y = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
        ]
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
