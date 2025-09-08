"""
Unit tests for database module
"""

import unittest
from unittest.mock import Mock, patch
from config.database import MongoDBConfig

class TestDatabaseConfig(unittest.TestCase):
    """Тесты конфигурации базы данных"""
    
    def test_default_uri(self):
        """Тест URI по умолчанию"""
        config = MongoDBConfig()
        self.assertEqual(config.uri, "mongodb://localhost:27017/")
    
    def test_default_db_name(self):
        """Тест имени БД по умолчанию"""
        config = MongoDBConfig()
        self.assertEqual(config.db_name, "hydra_metrics")
    
    @patch('os.getenv')
    def test_custom_uri(self, mock_getenv):
        """Тест кастомного URI"""
        mock_getenv.return_value = "mongodb://custom:27017/"
        config = MongoDBConfig()
        self.assertEqual(config.uri, "mongodb://custom:27017/")
    
    @patch('os.getenv')
    def test_custom_db_name(self, mock_getenv):
        """Тест кастомного имени БД"""
        mock_getenv.return_value = "custom_db"
        config = MongoDBConfig()
        self.assertEqual(config.db_name, "custom_db")