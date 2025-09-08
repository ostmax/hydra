# scripts/prepare_ml_data.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from config.database import MongoDBConfig
from src.data.processors.feature_engineer import FeatureEngineer

def prepare_ml_data():
    """Prepare data for machine learning"""
    print("📊 Preparing data for ML...")
    
    # Load data from MongoDB
    db = MongoDBConfig()
    db.connect()
    
    data = list(db.database["BTCUSDT"].find().sort("timestamp", 1))
    df = pd.DataFrame(data)
    
    print(f"📈 Loaded {len(df)} records for ML preparation")
    
    # Feature engineering
    engineer = FeatureEngineer()
    ml_data = engineer.process(df)
    
    print(f"🎯 ML features shape: {ml_data.shape}")
    print(f"📋 Features: {list(ml_data.columns)}")
    
    # Save prepared data
    ml_data.to_csv("data/ml_ready_data.csv", index=False)
    print("💾 ML data saved to data/ml_ready_data.csv")
    
    db.close()

if __name__ == "__main__":
    prepare_ml_data()