# create_init_files.py
import os

# Папки где нужно создать __init__.py
folders = [
    'src',
    'src/core',
    'src/data',
    'src/data/collectors',
    'src/data/processors',
    'src/data/storage',
    'src/ml',
    'src/ml/training',
    'src/ml/inference',
    'src/ml/evaluation',
    'src/trading',
    'src/trading/signals',
    'src/trading/risk',
    'src/utils',
    'tests',
    'tests/unit',
    'tests/integration',
    'tests/performance'
]

for folder in folders:
    init_file = os.path.join(folder, '__init__.py')
    os.makedirs(os.path.dirname(init_file), exist_ok=True)
    with open(init_file, 'w') as f:
        f.write('')
    print(f'Created: {init_file}')

print("All __init__.py files created successfully!")