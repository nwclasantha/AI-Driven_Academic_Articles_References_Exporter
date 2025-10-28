"""
Worker Thread Pool Manager
Enterprise-level concurrent processing with progress tracking
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from PySide6 import QtCore
from .pdf_processor import PDFProcessor
from .reference_parser import ReferenceParser, ParsedReference
from .exporter import ExportManager
from .api_client import MetadataEnricher
from .database import DatabaseManager, Reference


class ProcessingResult:
    """Result of processing a single PDF"""
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.success = False
        self.references: List[ParsedReference] = []
        self.error: str = ""
        self.processing_time: float = 0.0
        self.enriched: bool = False


class ExtractionWorker(QtCore.QObject):
    """
    Worker thread for extraction tasks
    Emits signals for progress updates and results
    """

    # Signals
    progress = QtCore.Signal(int, int, str)  # current, total, status
    log_message = QtCore.Signal(str, str)  # level, message
    pdf_completed = QtCore.Signal(str, int, float)  # pdf_name, ref_count, time
    finished = QtCore.Signal(dict)  # summary statistics
    error = QtCore.Signal(str)  # error message

    def __init__(self, pdf_paths: List[Path], output_dir: Path, config: Dict[str, Any]):
        super().__init__()
        self.pdf_paths = pdf_paths
        self.output_dir = output_dir
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.pdf_processor = PDFProcessor(
            enable_ml=config.get('enable_ml_parsing', True),
            enable_ocr=config.get('enable_ocr', False)
        )
        self.parser = ReferenceParser(style=config.get('citation_style', 'ieee'))
        self.exporter = ExportManager()
        self.enricher = MetadataEnricher(
            enable_crossref=config.get('enable_crossref', True),
            enable_doi=config.get('enable_doi_lookup', True)
        )
        self.db = DatabaseManager(config.get('db_path', 'data/references.db'))

        self._is_cancelled = False

    def cancel(self):
        """Cancel the extraction process"""
        self._is_cancelled = True
        self.log_message.emit('WARNING', 'Cancellation requested...')

    def run(self):
        """Main extraction process"""
        try:
            self.log_message.emit('INFO', f'Starting extraction of {len(self.pdf_paths)} PDFs')
            start_time = time.time()

            results = []
            total_refs = 0

            for idx, pdf_path in enumerate(self.pdf_paths, 1):
                if self._is_cancelled:
                    self.log_message.emit('WARNING', 'Extraction cancelled by user')
                    break

                # Update progress
                self.progress.emit(idx, len(self.pdf_paths), f"Processing {pdf_path.name}")
                self.log_message.emit('INFO', f'Processing: {pdf_path.name}')

                # Process single PDF
                result = self._process_pdf(pdf_path)
                results.append(result)

                if result.success:
                    total_refs += len(result.references)
                    self.pdf_completed.emit(
                        pdf_path.name,
                        len(result.references),
                        result.processing_time
                    )
                else:
                    self.log_message.emit('ERROR', f'Failed: {pdf_path.name} - {result.error}')

            # Calculate statistics
            elapsed = time.time() - start_time
            stats = {
                'total_pdfs': len(self.pdf_paths),
                'successful': sum(1 for r in results if r.success),
                'failed': sum(1 for r in results if not r.success),
                'total_references': total_refs,
                'elapsed_time': elapsed,
                'avg_time_per_pdf': elapsed / len(self.pdf_paths) if self.pdf_paths else 0
            }

            self.log_message.emit('INFO', f'Extraction complete: {total_refs} references from {stats["successful"]} PDFs')
            self.finished.emit(stats)

        except Exception as e:
            self.logger.exception(f'Worker error: {e}')
            self.error.emit(str(e))

    def _process_pdf(self, pdf_path: Path) -> ProcessingResult:
        """
        Process a single PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            ProcessingResult object
        """
        result = ProcessingResult(pdf_path)
        pdf_start = time.time()

        try:
            # Validate PDF
            is_valid, error = self.pdf_processor.validate_pdf(pdf_path)
            if not is_valid:
                result.error = error
                return result

            # Extract references section
            self.log_message.emit('DEBUG', f'Extracting text from {pdf_path.name}')
            refs_text = self.pdf_processor.extract_references_section(pdf_path)

            if not refs_text:
                result.error = "No references section found"
                return result

            self.log_message.emit('DEBUG', f'Extracted {len(refs_text)} characters')

            # Parse references
            self.log_message.emit('DEBUG', 'Parsing references')
            parsed_refs = self.parser.parse_references_section(refs_text)

            if not parsed_refs:
                result.error = "No references could be parsed"
                return result

            self.log_message.emit('INFO', f'Parsed {len(parsed_refs)} references')

            # Enrich metadata (if enabled)
            if self.config.get('enable_api_enrichment', False):
                self.log_message.emit('DEBUG', 'Enriching metadata via APIs')
                parsed_refs = self._enrich_references(parsed_refs)
                result.enriched = True

            # Save to database
            if self.config.get('save_to_database', True):
                self.log_message.emit('DEBUG', 'Saving to database')
                self._save_to_database(parsed_refs, pdf_path)

            # Export to file
            self._export_references(parsed_refs, pdf_path)

            result.references = parsed_refs
            result.success = True
            result.processing_time = time.time() - pdf_start

        except Exception as e:
            self.logger.exception(f'Error processing {pdf_path.name}: {e}')
            result.error = str(e)

        return result

    def _enrich_references(self, refs: List[ParsedReference]) -> List[ParsedReference]:
        """Enrich references with API metadata"""
        enriched = []

        for ref in refs:
            try:
                # Convert to dict for enrichment
                ref_dict = {
                    'title': ref.title,
                    'doi': ref.doi,
                    'authors': ref.authors,
                    'year': ref.year
                }

                # Enrich
                enriched_data = self.enricher.enrich_reference(ref_dict)

                # Update reference with enriched data
                if enriched_data.get('doi') and not ref.doi:
                    ref.doi = enriched_data['doi']
                if enriched_data.get('url') and not ref.url:
                    ref.url = enriched_data['url']
                if enriched_data.get('publisher') and not ref.publisher:
                    ref.publisher = enriched_data['publisher']

                enriched.append(ref)
            except Exception as e:
                self.logger.warning(f'Failed to enrich reference: {e}')
                enriched.append(ref)

        return enriched

    def _save_to_database(self, refs: List[ParsedReference], pdf_path: Path):
        """Save references to database"""
        for ref in refs:
            db_ref = Reference(
                pdf_source=pdf_path.name,
                ref_number=ref.ref_number,
                authors=ref.get_author_string(),
                title=ref.title,
                year=ref.year,
                journal=ref.journal,
                volume=ref.volume,
                issue=ref.issue,
                pages=ref.pages,
                doi=ref.doi,
                url=ref.url,
                abstract=ref.abstract,
                keywords=','.join(ref.keywords),
                citation_type=ref.citation_type,
                confidence_score=ref.confidence
            )
            self.db.add_reference(db_ref)

    def _export_references(self, refs: List[ParsedReference], pdf_path: Path):
        """Export references to configured formats"""
        export_format = self.config.get('default_export_format', 'bibtex')
        base_name = f"References_{pdf_path.stem}"

        output_path = self.output_dir / f"{base_name}.{self._get_extension(export_format)}"

        success = self.exporter.export(refs, output_path, export_format)

        if success:
            self.log_message.emit('INFO', f'Exported to: {output_path.name}')
        else:
            self.log_message.emit('ERROR', f'Export failed: {output_path.name}')

    def _get_extension(self, format: str) -> str:
        """Get file extension for format"""
        extensions = {
            'bibtex': 'bib',
            'ris': 'ris',
            'json': 'json',
            'csv': 'csv'
        }
        return extensions.get(format.lower(), 'bib')


class WorkerManager(QtCore.QObject):
    """
    Manages worker threads and task queue
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.current_worker: Optional[ExtractionWorker] = None
        self.current_thread: Optional[QtCore.QThread] = None

    def start_extraction(self, pdf_paths: List[Path], output_dir: Path,
                         config: Dict[str, Any]) -> ExtractionWorker:
        """
        Start extraction process in background thread

        Args:
            pdf_paths: List of PDF paths to process
            output_dir: Output directory
            config: Configuration dictionary

        Returns:
            ExtractionWorker instance
        """
        if self.current_thread and self.current_thread.isRunning():
            self.logger.warning('Worker already running')
            return self.current_worker

        # Create worker and thread
        self.current_worker = ExtractionWorker(pdf_paths, output_dir, config)
        self.current_thread = QtCore.QThread()

        # Move worker to thread
        self.current_worker.moveToThread(self.current_thread)

        # Connect signals
        self.current_thread.started.connect(self.current_worker.run)
        self.current_worker.finished.connect(self.current_thread.quit)
        self.current_worker.finished.connect(self._on_finished)

        # Start thread
        self.current_thread.start()

        self.logger.info('Extraction worker started')
        return self.current_worker

    def cancel_extraction(self):
        """Cancel current extraction"""
        if self.current_worker:
            self.current_worker.cancel()

    def _on_finished(self, stats: Dict[str, Any]):
        """Handle worker finished"""
        self.logger.info(f'Worker finished: {stats}')

    def is_running(self) -> bool:
        """Check if worker is running"""
        return self.current_thread and self.current_thread.isRunning()
