"""
Hydra Logger Configuration
Унифицированная система логирования для всего проекта
"""

import logging
import sys
from typing import Optional
from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)

class HydraLogger:
    """Кастомный логгер с цветным выводом"""
    
    def __init__(self, name: str = "hydra"):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Настройка формата и обработчиков"""
        if self.logger.handlers:
            return  # Уже настроен
        
        self.logger.setLevel(logging.INFO)
        
        # Форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(self._color_filter)
        
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
    
    def _color_filter(self, record: logging.LogRecord) -> bool:
        """Добавляем цвета к лог уровням"""
        if record.levelno == logging.INFO:
            record.msg = f"{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.CRITICAL:
            record.msg = f"{Fore.RED}{Style.BRIGHT}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.DEBUG:
            record.msg = f"{Fore.BLUE}{record.msg}{Style.RESET_ALL}"
        
        return True
    
    def info(self, msg: str, **kwargs) -> None:
        self.logger.info(msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        self.logger.warning(msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        self.logger.error(msg, **kwargs)
    
    def debug(self, msg: str, **kwargs) -> None:
        self.logger.debug(msg, **kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        self.logger.critical(msg, **kwargs)

# Глобальный экземпляр логгера
logger = HydraLogger("hydra")

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Создает и настраивает логгер для модуля
    
    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования
    
    Returns:
        Настроенный логгер
    """
    module_logger = logging.getLogger(name)
    module_logger.setLevel(level)
    
    # Если нет обработчиков, добавляем
    if not module_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        module_logger.addHandler(handler)
        module_logger.propagate = False
    
    return module_logger

# Утилиты для логирования
def log_system_info(config) -> None:
    """Логирование информации о системе"""
    logger.info("=" * 50)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 50)
    logger.info(f"RAM: {config.total_ram_gb} GB")
    logger.info(f"CPU: {config.cpu_cores}c/{config.logical_cores}t")
    logger.info(f"GPU: {'Yes' if config.has_gpu else 'No'}")
    logger.info(f"Mode: {'Laptop' if config.is_laptop else 'Desktop'}")
    logger.info("=" * 50)

if __name__ == "__main__":
    # Тестирование логгера
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.debug("Debug message")