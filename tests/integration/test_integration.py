"""
Integration tests for Hydra core components
"""

import unittest
from datetime import datetime

from src.core.system_config import SystemConfig
from src.core.data_manager import DataManager
from src.utils.logger import setup_logger
from config.database import MongoDBConfig

class TestIntegration(unittest.TestCase):
    """Тесты интеграции основных компонентов"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.logger = setup_logger("test_integration")
        self.config = SystemConfig()
        self.data_manager = DataManager()
    
    def test_system_config_integration(self):
        """Тест интеграции системной конфигурации"""
        self.logger.info("Testing system configuration integration")
        
        # Проверяем что конфигурация загрузилась
        self.assertIsNotNone(self.config)
        self.assertGreater(self.config.total_ram_gb, 0)
        self.assertGreater(self.config.cpu_cores, 0)
        self.assertIn('historical', self.config.batch_sizes)
        
        self.logger.info(f"Config: {self.config.total_ram_gb}GB RAM, {self.config.cpu_cores} cores")
    
    def test_logger_integration(self):
        """Тест интеграции логгера"""
        self.logger.info("Info message test")
        self.logger.warning("Warning message test")
        self.logger.error("Error message test")
        
        # Логгер должен работать без ошибок
        self.assertTrue(True)
    
    def test_database_connection(self):
        """Тест подключения к MongoDB"""
        self.logger.info("Testing MongoDB connection")
        
        db_config = MongoDBConfig()
        connection_success = db_config.connect()
        
        if connection_success:
            self.logger.info("✅ MongoDB connection successful")
            db_config.close()
        else:
            self.logger.warning("⚠️ MongoDB not available, skipping test")
            self.skipTest("MongoDB not available")
    
    def test_data_manager_basic(self):
        """Тест базовой функциональности DataManager"""
        self.logger.info("Testing DataManager basic functionality")
        
        # Проверяем что менеджер инициализировался
        self.assertIsNotNone(self.data_manager)
        self.assertIsNotNone(self.data_manager.config)
        self.assertIsNotNone(self.data_manager.realtime_queues)
        
        # Проверяем очереди
        self.assertIn('metrics', self.data_manager.realtime_queues)
        self.assertIn('signals', self.data_manager.realtime_queues)
        self.assertIn('errors', self.data_manager.realtime_queues)
    
    def test_config_and_manager_integration(self):
        """Тест интеграции конфигурации и менеджера данных"""
        self.logger.info("Testing config-manager integration")
        
        # Конфиг менеджера должен совпадать с глобальным конфигом
        self.assertEqual(self.data_manager.config.total_ram_gb, self.config.total_ram_gb)
        self.assertEqual(self.data_manager.config.cpu_cores, self.config.cpu_cores)
        
        # Настройки батчей должны быть согласованы
        self.assertEqual(
            self.data_manager.config.batch_sizes['historical'],
            self.config.batch_sizes['historical']
        )

def run_integration_tests():
    """Запуск интеграционных тестов"""
    print("🚀 Running Hydra Integration Tests")
    print("=" * 50)
    
    # Создаем test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
    else:
        print("❌ Some tests failed")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_integration_tests()