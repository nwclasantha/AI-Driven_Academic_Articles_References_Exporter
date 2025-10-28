"""
IEEE Reference Extractor - Enterprise Edition
Classes package initialization
"""

__version__ = "3.0.0"
__author__ = "IEEE Reference Extractor Team"

from .config import ConfigManager, AppConfig
from .database import DatabaseManager, Reference
from .logger import LoggerManager, PerformanceLogger
from .pdf_processor import PDFProcessor, TextBlock, PDFMetadata
from .reference_parser import ReferenceParser, ParsedReference
from .api_client import CrossRefClient, DOIClient, MetadataEnricher
from .exporter import ExportManager, BibTeXExporter, RISExporter, JSONExporter, CSVExporter
from .worker import WorkerManager, ExtractionWorker
from .gui import MainWindow

__all__ = [
    # Config
    'ConfigManager',
    'AppConfig',

    # Database
    'DatabaseManager',
    'Reference',

    # Logging
    'LoggerManager',
    'PerformanceLogger',

    # PDF Processing
    'PDFProcessor',
    'TextBlock',
    'PDFMetadata',

    # Parsing
    'ReferenceParser',
    'ParsedReference',

    # API
    'CrossRefClient',
    'DOIClient',
    'MetadataEnricher',

    # Export
    'ExportManager',
    'BibTeXExporter',
    'RISExporter',
    'JSONExporter',
    'CSVExporter',

    # Worker
    'WorkerManager',
    'ExtractionWorker',

    # GUI
    'MainWindow',
]
