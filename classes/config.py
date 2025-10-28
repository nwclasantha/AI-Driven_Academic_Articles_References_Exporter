"""
Configuration Management System
Enterprise-level configuration with validation and persistence
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class AppConfig:
    """Main application configuration"""
    # Directories
    input_dir: str = ""
    output_dir: str = ""
    cache_dir: str = "cache"
    log_dir: str = "logs"
    db_path: str = "data/references.db"

    # Processing settings
    max_workers: int = 4
    batch_size: int = 10
    timeout_seconds: int = 300

    # Parser settings
    similarity_threshold: float = 0.8
    min_confidence_score: float = 0.6
    extract_abstracts: bool = True
    extract_keywords: bool = True

    # API settings
    enable_crossref: bool = True
    enable_doi_lookup: bool = True
    enable_google_scholar: bool = False
    api_rate_limit: int = 5  # requests per second
    api_timeout: int = 10

    # Export settings
    default_export_format: str = "bibtex"
    citation_style: str = "ieee"
    combine_outputs: bool = False
    include_abstracts: bool = True

    # UI settings
    theme: str = "dark_teal"
    window_width: int = 1400
    window_height: int = 900
    font_size: int = 10
    auto_save: bool = True
    show_preview: bool = True

    # Advanced features
    enable_ml_parsing: bool = True
    enable_ocr: bool = False
    enable_plugins: bool = True
    check_for_updates: bool = True

    # Logging
    log_level: str = "INFO"
    max_log_size_mb: int = 10
    log_retention_days: int = 30

    # Metadata
    version: str = "3.0.0"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class ConfigManager:
    """
    Enterprise configuration manager with validation and persistence
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/settings.json")
        self.config: AppConfig = AppConfig()
        self.logger = logging.getLogger(__name__)
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Create configuration directory if it doesn't exist"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppConfig:
        """
        Load configuration from file

        Returns:
            AppConfig: Loaded configuration
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = AppConfig(**data)
                    self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.info("No config file found, using defaults")
                self.save()  # Create default config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.config = AppConfig()  # Fall back to defaults

        return self.config

    def save(self) -> bool:
        """
        Save configuration to file

        Returns:
            bool: True if successful
        """
        try:
            self.config.last_updated = datetime.now().isoformat()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False

    def update(self, **kwargs) -> bool:
        """
        Update configuration values

        Args:
            **kwargs: Configuration values to update

        Returns:
            bool: True if successful
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    self.logger.warning(f"Unknown config key: {key}")
            return self.save()
        except Exception as e:
            self.logger.error(f"Failed to update config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return getattr(self.config, key, default)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration values

        Returns:
            tuple: (is_valid, list of error messages)
        """
        errors = []

        # Validate numeric ranges
        if self.config.max_workers < 1 or self.config.max_workers > 32:
            errors.append("max_workers must be between 1 and 32")

        if self.config.similarity_threshold < 0 or self.config.similarity_threshold > 1:
            errors.append("similarity_threshold must be between 0 and 1")

        if self.config.min_confidence_score < 0 or self.config.min_confidence_score > 1:
            errors.append("min_confidence_score must be between 0 and 1")

        # Validate paths
        if self.config.input_dir and not Path(self.config.input_dir).exists():
            errors.append(f"Input directory does not exist: {self.config.input_dir}")

        # Validate enums
        valid_formats = ["bibtex", "ris", "endnote", "json", "csv"]
        if self.config.default_export_format not in valid_formats:
            errors.append(f"Invalid export format: {self.config.default_export_format}")

        valid_styles = ["ieee", "apa", "mla", "chicago", "harvard"]
        if self.config.citation_style not in valid_styles:
            errors.append(f"Invalid citation style: {self.config.citation_style}")

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config.log_level not in valid_log_levels:
            errors.append(f"Invalid log level: {self.config.log_level}")

        return (len(errors) == 0, errors)

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values

        Returns:
            bool: True if successful
        """
        self.config = AppConfig()
        return self.save()

    def export_config(self, path: Path) -> bool:
        """
        Export configuration to a different file

        Args:
            path: Export destination path

        Returns:
            bool: True if successful
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2)
            self.logger.info(f"Configuration exported to {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export config: {e}")
            return False

    def import_config(self, path: Path) -> bool:
        """
        Import configuration from a file

        Args:
            path: Import source path

        Returns:
            bool: True if successful
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.config = AppConfig(**data)
            self.logger.info(f"Configuration imported from {path}")
            return self.save()
        except Exception as e:
            self.logger.error(f"Failed to import config: {e}")
            return False
