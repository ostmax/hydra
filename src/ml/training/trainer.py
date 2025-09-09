# src/ml/training/trainer.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import lightgbm as lgb
import joblib
from typing import Dict, Any, Tuple
import numpy as np

class MLTrainer:
    """Тренер ML моделей"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.best_model: Any = None
        
    def train_models(self, X_train, y_train, X_test, y_test) -> Dict[str, Dict]:
        """Обучение нескольких моделей"""
        results = {}
        
        # 1. Random Forest
        print("🌲 Training Random Forest...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf_model.fit(X_train, y_train)
        self.models['random_forest'] = rf_model
        results['random_forest'] = self._evaluate_model(rf_model, X_test, y_test)
        
        # 2. XGBoost
        print("🚀 Training XGBoost...")
        xgb_model = xgb.XGBClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        xgb_model.fit(X_train, y_train)
        self.models['xgboost'] = xgb_model
        results['xgboost'] = self._evaluate_model(xgb_model, X_test, y_test)
        
        # 3. LightGBM
        print("💡 Training LightGBM...")
        lgb_model = lgb.LGBMClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        lgb_model.fit(X_train, y_train)
        self.models['lightgbm'] = lgb_model
        results['lightgbm'] = self._evaluate_model(lgb_model, X_test, y_test)
        
        # 4. Logistic Regression (baseline)
        print("📊 Training Logistic Regression...")
        lr_model = LogisticRegression(random_state=42, n_jobs=-1)
        lr_model.fit(X_train, y_train)
        self.models['logistic_regression'] = lr_model
        results['logistic_regression'] = self._evaluate_model(lr_model, X_test, y_test)
        
        # Выбираем лучшую модель
        self._select_best_model(results)
        
        return results
    
    def _evaluate_model(self, model, X_test, y_test) -> Dict[str, float]:
        """Оценка модели"""
        y_pred = model.predict(X_test)
        
        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0)
        }
    
    def _select_best_model(self, results: Dict[str, Dict]):
        """Выбор лучшей модели по F1-score"""
        best_model_name = max(results.items(), key=lambda x: x[1]['f1'])[0]
        self.best_model = self.models[best_model_name]
        print(f"🏆 Best model: {best_model_name}")
    
    def save_model(self, model_name: str, path: str):
        """Сохранение модели"""
        joblib.dump(self.models[model_name], path)
        print(f"💾 Model {model_name} saved to {path}")
    
    def save_best_model(self, path: str):
        """Сохранение лучшей модели"""
        if self.best_model:
            joblib.dump(self.best_model, path)
            print(f"💾 Best model saved to {path}")