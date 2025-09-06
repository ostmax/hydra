"""
Hydra System Configuration - Автоматическое определение возможностей железа
"""

import psutil
import platform
import subprocess
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('system_config')

@dataclass
class SystemConfig:
    """Автоматическая конфигурация системы на основе железа"""
    
    # Основные характеристики
    total_ram_gb: float = field(init=False)
    cpu_cores: int = field(init=False)
    logical_cores: int = field(init=False)
    cpu_frequency: float = field(init=False)
    has_gpu: bool = field(init=False)
    gpu_info: Optional[Dict[str, Any]] = field(init=False)
    os_type: str = field(init=False)
    is_laptop: bool = field(init=False)
    
    # Производные настройки
    max_workers: int = field(init=False)
    batch_sizes: Dict[str, int] = field(init=False)
    memory_limits: Dict[str, int] = field(init=False)
    use_gpu_acceleration: bool = field(init=False)
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        self._detect_hardware()
        self._calculate_optimized_settings()
        self._log_system_info()
    
    def _detect_hardware(self) -> None:
        """Обнаружение hardware характеристик"""
        try:
            # Память
            virtual_memory = psutil.virtual_memory()
            self.total_ram_gb = round(virtual_memory.total / (1024 ** 3), 2)
            
            # CPU
            self.cpu_cores = psutil.cpu_count(logical=False) or 1
            self.logical_cores = psutil.cpu_count(logical=True) or 1
            cpu_freq = psutil.cpu_freq()
            self.cpu_frequency = cpu_freq.current if cpu_freq else 0
            
            # GPU
            self.has_gpu, self.gpu_info = self._detect_gpu()
            
            # OS и тип устройства
            self.os_type = platform.system()
            self.is_laptop = self._detect_if_laptop()
            
        except Exception as e:
            logger.error(f"Ошибка определения железа: {e}")
            self._set_defaults()
    
    def _detect_gpu(self) -> tuple:
        """Обнаружение GPU и его характеристик"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Берем первую GPU
                gpu_info = {
                    'name': gpu.name,
                    'memory_total': gpu.memoryTotal,
                    'memory_free': gpu.memoryFree,
                    'driver': gpu.driver,
                    'temperature': gpu.temperature
                }
                return True, gpu_info
        except ImportError:
            logger.warning("GPUtil не установлен, GPU не будет обнаружена")
        except Exception as e:
            logger.warning(f"Ошибка обнаружения GPU: {e}")
        
        return False, None
    
    def _detect_if_laptop(self) -> bool:
        """Определяем, ноутбук это или десктоп"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["powercfg", "/batteryreport", "/output", "NUL"],
                    capture_output=True, text=True, timeout=10,
                    shell=True
                )
                return result.returncode == 0
            return False
        except:
            return False
    
    def _calculate_optimized_settings(self) -> None:
        """Расчет оптимизированных настроек на основе железа"""
        
        # Максимальное количество worker процессов
        if self.total_ram_gb >= 32:  # Сервер
            self.max_workers = max(1, self.logical_cores - 4)
        elif self.total_ram_gb >= 16:  # Мощный ПК
            self.max_workers = max(1, self.logical_cores - 2)
        else:  # Ноутбук
            self.max_workers = max(1, min(4, self.logical_cores - 1))
        
        # Размеры батчей для обработки
        if self.total_ram_gb >= 32:
            self.batch_sizes = {
                'historical': 50000,
                'realtime': 2000,
                'ml_training': 2048,
                'ml_inference': 1024
            }
        elif self.total_ram_gb >= 16:
            self.batch_sizes = {
                'historical': 25000,
                'realtime': 1000,
                'ml_training': 1024,
                'ml_inference': 512
            }
        else:  # Ноутбук 8GB
            self.batch_sizes = {
                'historical': 10000,
                'realtime': 500,
                'ml_training': 512,
                'ml_inference': 256
            }
        
        # Лимиты памяти для кэширования (в MB)
        if self.total_ram_gb >= 32:
            self.memory_limits = {
                'data_cache': 8192,  # 8GB
                'model_cache': 4096,  # 4GB
                'max_dataset_size': 16384  # 16GB
            }
        elif self.total_ram_gb >= 16:
            self.memory_limits = {
                'data_cache': 4096,  # 4GB
                'model_cache': 2048,  # 2GB
                'max_dataset_size': 8192  # 8GB
            }
        else:
            self.memory_limits = {
                'data_cache': 1024,  # 1GB
                'model_cache': 512,   # 0.5GB
                'max_dataset_size': 2048  # 2GB
            }
        
        # Использовать ли GPU ускорение
        self.use_gpu_acceleration = self.has_gpu and self.total_ram_gb >= 8
    
    def _set_defaults(self) -> None:
        """Установка значений по умолчанию при ошибках"""
        self.total_ram_gb = 8.0
        self.cpu_cores = 4
        self.logical_cores = 8
        self.cpu_frequency = 2.1
        self.has_gpu = False
        self.gpu_info = None
        self.os_type = "Unknown"
        self.is_laptop = True
        self._calculate_optimized_settings()
    
    def _log_system_info(self) -> None:
        """Логирование информации о системе"""
        logger.info("=" * 50)
        logger.info("HYDRA SYSTEM CONFIGURATION DETECTED")
        logger.info("=" * 50)
        logger.info(f"Total RAM: {self.total_ram_gb} GB")
        logger.info(f"CPU Cores: {self.cpu_cores} physical, {self.logical_cores} logical")
        logger.info(f"CPU Frequency: {self.cpu_frequency} GHz")
        logger.info(f"Has GPU: {self.has_gpu}")
        
        if self.has_gpu and self.gpu_info:
            logger.info(f"GPU: {self.gpu_info['name']}")
            logger.info(f"GPU Memory: {self.gpu_info['memory_total']} MB")
        
        logger.info(f"OS: {self.os_type}")
        logger.info(f"Is Laptop: {self.is_laptop}")
        logger.info(f"Max Workers: {self.max_workers}")
        logger.info(f"Use GPU Acceleration: {self.use_gpu_acceleration}")
        logger.info("=" * 50)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Возвращает сводку конфигурации"""
        return {
            'hardware': {
                'total_ram_gb': self.total_ram_gb,
                'cpu_cores': self.cpu_cores,
                'logical_cores': self.logical_cores,
                'cpu_frequency': self.cpu_frequency,
                'has_gpu': self.has_gpu,
                'gpu_info': self.gpu_info,
                'os_type': self.os_type,
                'is_laptop': self.is_laptop
            },
            'optimization': {
                'max_workers': self.max_workers,
                'batch_sizes': self.batch_sizes,
                'memory_limits': self.memory_limits,
                'use_gpu_acceleration': self.use_gpu_acceleration
            }
        }
    
    def should_use_simple_mode(self) -> bool:
        """Нужно ли использовать упрощенный режим"""
        return self.total_ram_gb < 16 or self.cpu_cores < 6
    
    def get_recommended_ml_framework(self) -> str:
        """Рекомендуемый ML фреймворк"""
        if self.has_gpu and self.total_ram_gb >= 16:
            return "tensorflow"
        elif self.total_ram_gb >= 8:
            return "sklearn"
        else:
            return "sklearn"

# Глобальный экземпляр конфигурации
CONFIG = SystemConfig()

if __name__ == "__main__":
    # Тестирование конфигурации
    config = SystemConfig()
    print("Configuration Summary:")
    import json
    print(json.dumps(config.get_config_summary(), indent=2))