"""
Data Manager - Централизованное управление данными Hydra
"""

import time
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque

from src.core.system_config import CONFIG
from src.utils.logger import setup_logger
from config.database import get_collection

# Логгер
logger = setup_logger(__name__)

class DataManager:
    """Менеджер данных с оптимизацией под железо"""
    
    def __init__(self):
        self.config = CONFIG
        self.cache = {}
        self.cache_size_limit = self.config.memory_limits['data_cache']
        self.current_cache_size = 0
        
        # Очереди для реального времени
        self.realtime_queues = {
            'metrics': deque(maxlen=1000),
            'signals': deque(maxlen=500),
            'errors': deque(maxlen=100)
        }
        
        logger.info(f"DataManager initialized with cache limit: {self.cache_size_limit}MB")
    
    def _get_collection(self, collection_name: str):
        """Получение коллекции с обработкой ошибок"""
        try:
            return get_collection(collection_name)
        except Exception as e:
            logger.error(f"Failed to get collection {collection_name}: {e}")
            return None
    
    def save_metrics(self, metrics_data: Dict[str, Any], symbol: str = "BTCUSDT") -> bool:
        """
        Сохранение метрик в MongoDB
        
        Args:
            metrics_data: Данные метрик
            symbol: Торговый символ
        
        Returns:
            True если успешно, False если ошибка
        """
        try:
            collection = self._get_collection(symbol.lower())
            if not collection:
                return False
            
            document = {
                'timestamp': datetime.utcnow(),
                'symbol': symbol,
                'metrics': metrics_data,
                'processed': False,
                'created_at': datetime.utcnow()
            }
            
            # Вставка с оптимизацией батча
            result = collection.insert_one(document)
            
            # Добавляем в реальное время очередь
            self.realtime_queues['metrics'].append({
                'id': str(result.inserted_id),
                'timestamp': document['timestamp'],
                'symbol': symbol,
                **metrics_data
            })
            
            logger.debug(f"Metrics saved for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            self.realtime_queues['errors'].append({
                'timestamp': datetime.utcnow(),
                'error': str(e),
                'operation': 'save_metrics'
            })
            return False
    
    def get_latest_metrics(self, symbol: str = "BTCUSDT", limit: int = 10) -> List[Dict]:
        """
        Получение последних метрик
        
        Args:
            symbol: Торговый символ
            limit: Количество записей
        
        Returns:
            Список последних метрик
        """
        try:
            collection = self._get_collection(symbol.lower())
            if not collection:
                return []
            
            cursor = collection.find(
                {'symbol': symbol},
                sort=[('timestamp', -1)],
                limit=limit
            )
            
            metrics = []
            for doc in cursor:
                metrics.append({
                    'timestamp': doc['timestamp'],
                    'metrics': doc['metrics'],
                    'id': str(doc['_id'])
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return []
    
    def get_historical_data(self, symbol: str, 
                          start_time: datetime, 
                          end_time: datetime,
                          batch_size: Optional[int] = None) -> pd.DataFrame:
        """
        Получение исторических данных батчами
        
        Args:
            symbol: Торговый символ
            start_time: Начальное время
            end_time: Конечное время
            batch_size: Размер батча (авто если None)
        
        Returns:
            DataFrame с историческими данными
        """
        if batch_size is None:
            batch_size = self.config.batch_sizes['historical']
        
        try:
            collection = self._get_collection(symbol.lower())
            if not collection:
                return pd.DataFrame()
            
            all_data = []
            current_start = start_time
            
            while current_start < end_time:
                current_end = min(current_start + timedelta(hours=24), end_time)
                
                cursor = collection.find({
                    'symbol': symbol,
                    'timestamp': {
                        '$gte': current_start,
                        '$lt': current_end
                    }
                }, batch_size=batch_size)
                
                batch_data = list(cursor)
                if batch_data:
                    all_data.extend(batch_data)
                
                current_start = current_end
                
                # Пауза для избежания перегрузки
                time.sleep(0.1)
            
            if not all_data:
                return pd.DataFrame()
            
            # Конвертируем в DataFrame
            df = pd.DataFrame([{
                'timestamp': doc['timestamp'],
                'symbol': doc['symbol'],
                **doc['metrics']
            } for doc in all_data])
            
            logger.info(f"Loaded {len(df)} historical records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return pd.DataFrame()
    
    def cleanup_old_data(self, older_than_days: int = 30) -> int:
        """
        Очистка старых данных
        
        Args:
            older_than_days: Удалять данные старше X дней
        
        Returns:
            Количество удаленных документов
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            # Получаем все коллекции
            client = get_mongo_client()
            db = client[os.getenv("MONGODB_DB_NAME", "hydra_metrics")]
            
            deleted_count = 0
            for collection_name in db.list_collection_names():
                collection = db[collection_name]
                result = collection.delete_many({
                    'timestamp': {'$lt': cutoff_date}
                })
                deleted_count += result.deleted_count
            
            logger.info(f"Cleaned up {deleted_count} old documents")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up data: {e}")
            return 0
    
    def get_realtime_queue(self, queue_name: str) -> deque:
        """
        Получение очереди реального времени
        
        Args:
            queue_name: Имя очереди (metrics, signals, errors)
        
        Returns:
            Очередь данных
        """
        return self.realtime_queues.get(queue_name, deque())
    
    def clear_cache(self) -> None:
        """Очистка кэша"""
        self.cache.clear()
        self.current_cache_size = 0
        logger.info("Data cache cleared")

# Глобальный экземпляр менеджера данных
data_manager = DataManager()

if __name__ == "__main__":
    # Тестирование менеджера данных
    dm = DataManager()
    
    # Тестовые данные
    test_metrics = {
        'price': 50000.0,
        'volume': 1000.0,
        'rsi': 55.5,
        'sma': 49000.0
    }
    
    # Сохранение тестовых данных
    success = dm.save_metrics(test_metrics, "BTCUSDT")
    print(f"Save successful: {success}")
    
    # Получение последних данных
    latest = dm.get_latest_metrics("BTCUSDT", 5)
    print(f"Latest metrics: {len(latest)} records")