# scripts/analyze_old_data.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import MongoDBConfig

def analyze_old_data():
    """Analyze existing data in MongoDB"""
    print("🔍 Analyzing existing data...")
    
    db = MongoDBConfig()
    if not db.connect():
        print("❌ Cannot connect to MongoDB")
        return
    
    try:
        collection = db.database["BTCUSDT"]
        
        # Basic stats
        count = collection.count_documents({})
        print(f"📊 Total documents: {count:,}")
        
        # Check document structure
        sample = collection.find_one()
        if sample:
            print("📋 Sample document structure:")
            print(f"Keys: {list(sample.keys())}")
            
            if 'metrics' in sample:
                print(f"📈 Metrics keys: {list(sample['metrics'].keys())}")
            
            print(f"⏰ Latest timestamp: {sample.get('time')}")
        
        # Check time range
        oldest = collection.find_one(sort=[("time", 1)])
        newest = collection.find_one(sort=[("time", -1)])
        
        if oldest and newest:
            print(f"📅 Time range: {oldest['time']} to {newest['time']}")
            
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze_old_data()