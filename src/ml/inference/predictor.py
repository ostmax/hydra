"""
Predictor - предсказания моделей
"""

import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List

class MLPredictor:
    """ML предсказания"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        
    def load_model(self, model_path: str, scaler_path: str = None):
        """Загрузка модели и скейлеров"""
        self.model = joblib.load(model_path)
        if scaler_path:
            self.scaler = joblib.load(scaler_path)
    
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Предсказание на новых данных"""
        if self.scaler:
            features_scaled = self.scaler.transform(features)
        else:
            features_scaled = features
            
        return self.model.predict(features_scaled)
    
    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        """Предсказание вероятностей"""
        if self.scaler:
            features_scaled = self.scaler.transform(features)
        else:
            features_scaled = features
            
        return self.model.predict_proba(features_scaled)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Важность фич"""
        if hasattr(self.model, 'feature_importances_'):
            return dict(zip(
                [f"feature_{i}" for i in range(len(self.model.feature_importances_))],
                self.model.feature_importances_
            ))
        return {}