#!/usr/bin/env python3
"""
IEEE Reference Extractor - Enterprise Edition v3.0
Main entry point for the application

Features:
- Advanced PDF processing with column-aware extraction
- ML-enhanced reference parsing
- API integration for metadata enrichment (CrossRef, DOI)
- Multiple export formats (BibTeX, RIS, JSON, CSV)
- SQLite database for reference management
- Modern GUI with real-time progress tracking
- Comprehensive logging system
"""

import sys
import logging
from pathlib import Path
from PySide6 import QtWidgets
from qt_material import apply_stylesheet

# Add classes directory to path
sys.path.insert(0, str(Path(__file__).parent))

from classes.config import ConfigManager
from classes.logger import LoggerManager
from classes.gui import MainWindow


def setup_application():
    """
    Setup application environment

    Returns:
        tuple: (config_manager, logger_manager)
    """
    # Create necessary directories
    dirs = ['config', 'data', 'logs', 'cache', 'Output']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

    # Initialize configuration
    config_manager = ConfigManager()
    config = config_manager.load()

    # Initialize logging
    logger_manager = LoggerManager(
        log_dir=config.log_dir,
        app_name="IEEE_Extractor"
    )
    logger_manager.set_level(config.log_level)

    logger = logger_manager.get_logger()
    logger.info("="*60)
    logger.info("IEEE Reference Extractor - Enterprise Edition v3.0")
    logger.info("="*60)
    logger.info(f"Configuration loaded from: {config_manager.config_path}")
    logger.info(f"Database path: {config.db_path}")
    logger.info(f"Log directory: {config.log_dir}")

    # Validate configuration
    is_valid, errors = config_manager.validate()
    if not is_valid:
        logger.warning("Configuration validation errors:")
        for error in errors:
            logger.warning(f"  - {error}")

    # Cleanup old logs
    logger_manager.cleanup_old_logs(config.log_retention_days)

    return config_manager, logger_manager


def main():
    """
    Main application entry point
    """
    try:
        # Create Qt Application
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("IEEE Reference Extractor")
        app.setApplicationVersion("3.0.0")
        app.setOrganizationName("IEEE")

        # Setup application
        config_manager, logger_manager = setup_application()

        # Apply theme
        theme = config_manager.config.theme
        try:
            apply_stylesheet(app, theme=f'{theme}.xml')
            logger_manager.get_logger().info(f"Applied theme: {theme}")
        except Exception as e:
            logger_manager.get_logger().warning(f"Failed to apply theme: {e}")

        # Create and show main window
        window = MainWindow(config_manager, logger_manager)
        window.show()

        logger_manager.get_logger().info("Application started successfully")

        # Run application
        sys.exit(app.exec())

    except Exception as e:
        logging.exception(f"Fatal error: {e}")

        # Show error dialog if GUI is available
        try:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.setWindowTitle("Fatal Error")
            error_dialog.setText("A fatal error occurred:")
            error_dialog.setInformativeText(str(e))
            error_dialog.setDetailedText(f"Error type: {type(e).__name__}")
            error_dialog.exec()
        except:
            pass

        sys.exit(1)


if __name__ == '__main__':
    main()
