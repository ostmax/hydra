# scripts/verify_fresh_data.py (исправленная версия)
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from config.database import MongoDBConfig

def verify_fresh_data():
    """Verify the fresh data collection"""
    print("🔍 Verifying fresh data...")
    
    db = MongoDBConfig()
    if not db.connect():
        print("❌ Cannot connect to MongoDB")
        return
    
    try:
        # Check main collection
        main_count = db.database["BTCUSDT"].count_documents({})
        print(f"📊 BTCUSDT collection: {main_count} documents")
        
        # Check archive
        archive_count = db.database["BTCUSDT_archive"].count_documents({})
        print(f"📦 BTCUSDT_archive: {archive_count} documents")
        
        # Sample of new data - check both time and timestamp
        if main_count > 0:
            sample = db.database["BTCUSDT"].find_one(sort=[("timestamp", -1)])
            if sample:
                time_field = sample.get('time', 'N/A')
                timestamp_field = sample.get('timestamp', 'N/A')
                print(f"🆕 Latest time: {time_field}")
                print(f"🆕 Latest timestamp: {timestamp_field}")
                
                if 'metrics' in sample:
                    print(f"📈 Latest close price: {sample['metrics'].get('close')}")
                    
                # Show all keys for debugging
                print(f"🔑 Document keys: {list(sample.keys())}")
            else:
                print("ℹ️ No sample data found")
        
        print("✅ Verification completed!")
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_fresh_data()