# scripts/train_first_model.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

def train_model():
    """Train first ML model"""
    print("🤖 Training first ML model...")
    
    # Load prepared data
    df = pd.read_csv("data/ml_ready_data.csv")
    
    # Prepare features and target
    # Example: predict if price will go up (1) or down (0) next period
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    df = df.dropna()
    
    features = ['open', 'high', 'low', 'close', 'volume', 'returns', 'volatility']
    features = [f for f in features if f in df.columns]
    
    X = df[features]
    y = df['target']
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"📊 Train accuracy: {train_score:.3f}")
    print(f"📊 Test accuracy: {test_score:.3f}")
    
    # Save model
    joblib.dump(model, "models/first_model.pkl")
    print("💾 Model saved to models/first_model.pkl")

if __name__ == "__main__":
    train_model()