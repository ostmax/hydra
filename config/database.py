"""
MongoDB Configuration and Connection Management
"""

import os
from typing import Optional
from pymongo import MongoClient, database
from pymongo.errors import ConnectionFailure, ConfigurationError

from src.utils.logger import setup_logger

# Логгер
logger = setup_logger(__name__)

class MongoDBConfig:
    """Конфигурация и управление MongoDB подключениями"""
    
    def __init__(self):
        self.uri = self._get_connection_uri()
        self.db_name = self._get_database_name()
        self.client: Optional[MongoClient] = None
        self.database: Optional[database.Database] = None
    
    def _get_connection_uri(self) -> str:
        """Получение URI подключения из переменных окружения"""
        return os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    
    def _get_database_name(self) -> str:
        """Получение имени базы данных"""
        return os.getenv("MONGODB_DB_NAME", "hydra_metrics")
    
    def connect(self) -> bool:
        """Установка подключения к MongoDB"""
        try:
            self.client = MongoClient(
                self.uri,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000,
                maxPoolSize=10,
                minPoolSize=1
            )
            
            # Проверяем подключение
            self.client.admin.command('ping')
            self.database = self.client[self.db_name]
            
            logger.info(f"✅ Successfully connected to MongoDB: {self.db_name}")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
        except ConfigurationError as e:
            logger.error(f"❌ MongoDB configuration error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected MongoDB error: {e}")
            return False
    
    def get_collection(self, collection_name: str):
        """Получение коллекции из базы данных"""
        if not self.database:
            if not self.connect():
                raise ConnectionError("MongoDB connection not established")
        
        return self.database[collection_name]
    
    def close(self) -> None:
        """Закрытие подключения"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def __enter__(self):
        """Контекстный менеджер"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        self.close()

# Глобальный экземпляр конфигурации
mongodb_config = MongoDBConfig()

def get_mongo_client() -> MongoClient:
    """Получение MongoDB клиента"""
    if not mongodb_config.client:
        mongodb_config.connect()
    return mongodb_config.client

def get_database() -> database.Database:
    """Получение базы данных"""
    if not mongodb_config.database:
        mongodb_config.connect()
    return mongodb_config.database

def get_collection(collection_name: str):
    """Получение коллекции"""
    return mongodb_config.get_collection(collection_name)

if __name__ == "__main__":
    # Тестирование подключения
    with MongoDBConfig() as db:
        if db.connect():
            print("✅ MongoDB connection successful")
            print(f"Database: {db.db_name}")
            print(f"URI: {db.uri}")