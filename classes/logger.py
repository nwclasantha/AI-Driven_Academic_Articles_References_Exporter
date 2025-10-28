"""
Enterprise Logging System
Advanced logging with file rotation, filtering, and real-time monitoring
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from typing import Optional
from PySide6 import QtCore


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        return super().format(record)


class QtLogHandler(logging.Handler, QtCore.QObject):
    """
    Custom log handler that emits Qt signals
    Allows GUI to receive log messages in real-time
    """
    log_signal = QtCore.Signal(str, str)  # (level, message)

    def __init__(self):
        logging.Handler.__init__(self)
        QtCore.QObject.__init__(self)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_signal.emit(record.levelname, msg)
        except Exception:
            self.handleError(record)


class LoggerManager:
    """
    Enterprise logging manager with multiple handlers and rotation
    """

    def __init__(self, log_dir: str = "logs", app_name: str = "IEEE_Extractor"):
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.main_logger = None
        self.qt_handler = None
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging system"""
        # Create main logger
        self.main_logger = logging.getLogger(self.app_name)
        self.main_logger.setLevel(logging.DEBUG)
        self.main_logger.handlers.clear()

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.main_logger.addHandler(console_handler)

        # Main log file with rotation (10MB max, keep 5 backups)
        main_log_path = self.log_dir / f"{self.app_name}.log"
        file_handler = RotatingFileHandler(
            main_log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.main_logger.addHandler(file_handler)

        # Error log file (only errors and critical)
        error_log_path = self.log_dir / f"{self.app_name}_errors.log"
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.main_logger.addHandler(error_handler)

        # Daily rotating handler for archival
        daily_log_path = self.log_dir / f"{self.app_name}_daily.log"
        daily_handler = TimedRotatingFileHandler(
            daily_log_path,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(file_formatter)
        self.main_logger.addHandler(daily_handler)

        # Qt signal handler for GUI
        self.qt_handler = QtLogHandler()
        self.qt_handler.setLevel(logging.INFO)
        qt_formatter = logging.Formatter('%(message)s')
        self.qt_handler.setFormatter(qt_formatter)
        self.main_logger.addHandler(self.qt_handler)

        self.main_logger.info(f"Logging system initialized - {self.log_dir}")

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance

        Args:
            name: Logger name (defaults to app name)

        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f"{self.app_name}.{name}")
        return self.main_logger

    def set_level(self, level: str):
        """
        Set logging level

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level in level_map:
            self.main_logger.setLevel(level_map[level])
            self.main_logger.info(f"Log level set to {level}")

    def get_qt_handler(self) -> QtLogHandler:
        """Get Qt signal handler for GUI integration"""
        return self.qt_handler

    def cleanup_old_logs(self, days: int = 30):
        """
        Clean up log files older than specified days

        Args:
            days: Number of days to keep
        """
        import time
        cutoff = time.time() - (days * 86400)
        count = 0

        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff:
                try:
                    log_file.unlink()
                    count += 1
                except Exception as e:
                    self.main_logger.error(f"Failed to delete old log {log_file}: {e}")

        if count > 0:
            self.main_logger.info(f"Cleaned up {count} old log files")

    def get_log_stats(self) -> dict:
        """Get logging statistics"""
        stats = {
            'log_directory': str(self.log_dir),
            'total_log_files': len(list(self.log_dir.glob("*.log*"))),
            'total_size_mb': 0.0,
            'handlers': len(self.main_logger.handlers),
            'log_level': logging.getLevelName(self.main_logger.level)
        }

        # Calculate total size
        total_bytes = sum(f.stat().st_size for f in self.log_dir.glob("*.log*"))
        stats['total_size_mb'] = round(total_bytes / (1024 * 1024), 2)

        return stats

    def export_recent_logs(self, output_file: Path, lines: int = 1000) -> bool:
        """
        Export recent log entries to a file

        Args:
            output_file: Output file path
            lines: Number of recent lines to export

        Returns:
            True if successful
        """
        try:
            main_log = self.log_dir / f"{self.app_name}.log"
            if not main_log.exists():
                return False

            with open(main_log, 'r', encoding='utf-8') as src:
                all_lines = src.readlines()

            recent_lines = all_lines[-lines:]

            with open(output_file, 'w', encoding='utf-8') as dst:
                dst.writelines(recent_lines)

            self.main_logger.info(f"Exported {len(recent_lines)} log lines to {output_file}")
            return True
        except Exception as e:
            self.main_logger.error(f"Failed to export logs: {e}")
            return False


class PerformanceLogger:
    """
    Context manager for performance logging
    """

    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if exc_type:
            self.logger.error(f"Failed: {self.operation} after {elapsed:.2f}s - {exc_val}")
        else:
            self.logger.info(f"Completed: {self.operation} in {elapsed:.2f}s")


# Convenience functions
def log_function_call(func):
    """Decorator to log function calls"""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Completed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise

    return wrapper


def log_exception(logger: logging.Logger, message: str = "Exception occurred"):
    """Decorator to log exceptions"""
    import functools

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"{message} in {func.__name__}: {e}")
                raise

        return wrapper

    return decorator
