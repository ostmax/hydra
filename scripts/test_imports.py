#!/usr/bin/env python3
"""
Test script to check all imports
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

def test_imports():
    """Test all module imports"""
    modules_to_test = [
        "src.core.system_config",
        "src.utils.logger", 
        "config.database",
        "src.data.data_manager",
        "src.data.collectors.binance_collector",
        "src.data.collectors.glassnode_collector",
        "src.data.processors.feature_engineer",
        "src.data.processors.data_cleaner",
        "src.data.storers.mongo_storer",
        "src.data.storers.cache_storer"
    ]
    
    print("🧪 Testing module imports...")
    print("=" * 50)
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            print(f"⚠️  {module_name}: {e}")

if __name__ == "__main__":
    test_imports()