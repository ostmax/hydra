# scripts/archive_old_data.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import MongoDBConfig
from datetime import datetime

def archive_old_data():
    """Archive old data to separate collection"""
    print("📦 Archiving old data...")
    
    db = MongoDBConfig()
    if not db.connect():
        print("❌ Cannot connect to MongoDB")
        return
    
    try:
        source_collection = db.database["BTCUSDT"]
        target_collection = db.database["BTCUSDT_archive"]
        
        # Check if source collection exists and has data
        count = source_collection.count_documents({})
        if count == 0:
            print("ℹ️ No data to archive")
            return
        
        print(f"📊 Archiving {count} documents...")
        
        # Copy all documents to archive
        documents = list(source_collection.find({}))
        if documents:
            target_collection.insert_many(documents)
            print(f"✅ Archived {len(documents)} documents to BTCUSDT_archive")
        
        # Clear the original collection
        result = source_collection.delete_many({})
        print(f"🗑️ Cleared {result.deleted_count} documents from BTCUSDT")
        
        # Add archive metadata
        target_collection.insert_one({
            "archived_at": datetime.utcnow(),
            "original_count": count,
            "archive_note": "Old test data from previous version"
        })
        
        print("🎉 Archive completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during archiving: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    archive_old_data()