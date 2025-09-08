# scripts/fix_nan_imports.py
import re
from pathlib import Path

def fix_nan_imports():
    """Fix NaN imports in all Python files"""
    files_to_fix = [
        "src/data/processors/data_cleaner.py",
        "src/data/processors/feature_engineer.py", 
        "src/data/storers/mongo_storer.py",
        "src/data/storers/cache_storer.py",
        "src/data/data_manager.py"
    ]
    
    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            print(f"Fixing {file_path}...")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace from numpy import NaN
            new_content = re.sub(
                r'from numpy import NaN',
                'import numpy as np\nNaN = np.nan',
                content
            )
            
            # Replace other NaN patterns if any
            new_content = new_content.replace('NaN', 'np.nan')
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ Fixed {file_path}")

if __name__ == "__main__":
    fix_nan_imports()