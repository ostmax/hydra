#!/usr/bin/env python3
"""
Test script for data collection
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.data.data_manager import DataManager
from config.database import MongoDBConfig
import pandas as pd

def test_collection():
    """Test data collection pipeline"""
    print("🚀 Testing data collection pipeline...")
    
    # Test MongoDB connection
    print("🔌 Testing MongoDB connection...")
    db = MongoDBConfig()
    if db.connect():
        print("✅ MongoDB connected successfully!")
        db.close()
    else:
        print("❌ MongoDB connection failed")
        return
    
    # Test data collection
    print("📊 Testing Binance data collection...")
    dm = DataManager()
    
    try:
        # Test Binance collector
        btc_data = dm.collect_data(
            "binance", 
            symbol="BTCUSDT", 
            interval="1h", 
            limit=5
        )
        
        if not btc_data:
            print("❌ No data collected from Binance")
            return
        
        print(f"✅ Collected {len(btc_data)} BTC records")
        
        # Convert to DataFrame for better visualization
        df = pd.DataFrame(btc_data)
        print("\n📋 Sample data:")
        print(df[['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']].head())
        
        # Test processing
        print("\n⚙️ Testing data processing...")
        processed = dm.process_data(df, ["cleaning", "feature_engineering"])
        
        if processed is not None and not processed.empty:
            print(f"✅ Processed data shape: {processed.shape}")
            print("\n🎯 Added features:")
            new_features = [col for col in processed.columns if col not in df.columns]
            print(f"New features: {new_features[:10]}...")  # Show first 10 new features
        else:
            print("❌ Data processing failed")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_glassnode():
    """Test Glassnode collector (if API key available)"""
    print("\n🔗 Testing Glassnode collector...")
    
    dm = DataManager()
    glassnode = dm.collectors["glassnode"]
    
    # Check if API key is available
    if not glassnode.api_key:
        print("ℹ️ Glassnode API key not set, skipping test")
        return
    
    if glassnode.health_check():
        print("✅ Glassnode API is accessible")
        
        # Test fetching data
        try:
            data = glassnode.fetch_data(
                metric="market.price_usd.close",
                asset="btc",
                interval="24h",
                since=pd.Timestamp.now() - pd.Timedelta(days=7)
            )
            
            if data:
                print(f"✅ Collected {len(data)} Glassnode records")
            else:
                print("❌ No data from Glassnode")
                
        except Exception as e:
            print(f"❌ Glassnode error: {e}")
    else:
        print("❌ Glassnode API not accessible")

if __name__ == "__main__":
    print("=" * 60)
    print("HYDRA DATA COLLECTION TEST")
    print("=" * 60)
    
    test_collection()
    test_glassnode()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)