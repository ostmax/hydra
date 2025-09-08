# scripts/fresh_data_start.py
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем корень проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.data.data_manager import DataManager
from config.database import MongoDBConfig

async def main():
    print("🔄 Starting fresh data collection...")
    
    # 1. First, ensure collection is empty
    db = MongoDBConfig()
    if not db.connect():
        print("❌ Cannot connect to MongoDB")
        return
    
    try:
        collection = db.database["BTCUSDT"]
        count = collection.count_documents({})
        
        if count > 0:
            print(f"⚠️ Collection BTCUSDT still has {count} documents")
            choice = input("Clear collection? (y/n): ")
            if choice.lower() == 'y':
                result = collection.delete_many({})
                print(f"🗑️ Cleared {result.deleted_count} documents")
            else:
                print("❌ Aborting - collection not empty")
                return
    finally:
        db.close()
    
    # 2. Start fresh data collection
    dm = DataManager()
    
    print("📊 Collecting fresh historical data...")
    
    # Get realistic date range (last 1-2 years)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)  # 1 year history
    
    fresh_data = dm.collect_data(
        "binance",
        symbol="BTCUSDT",
        interval="1h",
        limit=1000,  # Start with smaller amount
        start_time=start_date,
        end_time=end_date
    )
    
    if not fresh_data:
        print("❌ No data collected from Binance")
        return
    
    print(f"✅ Collected {len(fresh_data)} fresh records")
    
    # Check timestamps
    if fresh_data and 'timestamp' in fresh_data[0]:
        print(f"📅 Time range: {fresh_data[0]['timestamp']} to {fresh_data[-1]['timestamp']}")
    
    # 3. Process and store
    print("⚙️ Processing data...")
    try:
        processed_data = dm.process_data(
            fresh_data,
            ["cleaning", "feature_engineering"]
        )
        
        print("💾 Saving to database...")
        success = dm.store_data(
            processed_data,
            "mongo",
            collection_name="BTCUSDT"
        )
        
        if success:
            print("🎉 Fresh data collection completed!")
            
            # Verify storage
            db.connect()
            new_count = db.database["BTCUSDT"].count_documents({})
            print(f"📊 New document count: {new_count}")
            db.close()
        else:
            print("❌ Failed to save data")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())