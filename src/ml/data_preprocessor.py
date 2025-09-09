import pandas as pd
import numpy as np
from typing import Tuple, Dict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

class MLDataPreprocessor:
    """Подготовка данных для ML моделей"""

    def __init__(self):
        self.scalers: Dict[str, StandardScaler] = {}
        self.feature_columns: list = []

    def prepare_training_data(self, df: pd.DataFrame,
                              target_column: str = "target",
                              test_size: float = 0.2,
                              random_state: int = 42) -> Tuple:
        print("🔧 Creating target variable...")
        df = self._create_target_variable(df, target_column)

        print("🔧 Selecting features...")
        X = self._select_features(df)
        y = df[target_column]

        print("🔧 Cleaning NaN values...")
        valid_indices = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_indices]
        y = y[valid_indices]

        print("🔧 Splitting train/test...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, shuffle=False
        )

        print("🔧 Scaling features...")
        X_train_scaled, X_test_scaled = self._scale_features(X_train, X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test

    def _create_target_variable(self, df: pd.DataFrame, target_column: str) -> pd.DataFrame:
        if "close" in df.columns:
            df[target_column] = (df["close"].shift(-1) > df["close"]).astype(int)
            return df.dropna()
        else:
            raise ValueError("Column 'close' not found in DataFrame")

    def _select_features(self, df: pd.DataFrame) -> pd.DataFrame:
        base_features = [
            "open", "high", "low", "close", "volume",
            "returns", "volatility", "rsi_14", "sma_20", "sma_50"
        ]
        available_features = [f for f in base_features if f in df.columns]
        self.feature_columns = available_features
        print(f"📋 Using features: {available_features}")
        return df[available_features]

    def _scale_features(self, X_train: pd.DataFrame, X_test: pd.DataFrame) -> Tuple:
        self.scalers["features"] = StandardScaler()
        X_train_scaled = self.scalers["features"].fit_transform(X_train)
        X_test_scaled = self.scalers["features"].transform(X_test)
        return X_train_scaled, X_test_scaled

    def save_scalers(self, path: str):
        joblib.dump(self.scalers, path)
        print(f"💾 Scalers saved to {path}")

    def load_scalers(self, path: str):
        self.scalers = joblib.load(path)


