"""
Database Layer - SQLite ORM for Reference Management
Enterprise-level data persistence with indexing and caching
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class Reference:
    """Reference data model"""
    id: Optional[int] = None
    pdf_source: str = ""
    ref_number: str = ""
    authors: str = ""
    title: str = ""
    year: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str = ""
    url: str = ""
    abstract: str = ""
    keywords: str = ""
    citation_type: str = "article"  # article, inproceedings, book, etc.
    confidence_score: float = 0.0
    verified: bool = False
    notes: str = ""
    tags: str = ""  # JSON array of tags
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reference':
        """Create from dictionary"""
        return cls(**data)


class DatabaseManager:
    """
    Enterprise database manager with connection pooling and transactions
    """

    def __init__(self, db_path: str = "data/references.db"):
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        """Create database directory if it doesn't exist"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Ensures proper connection handling and cleanup
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema"""
        schema = """
        CREATE TABLE IF NOT EXISTS "references" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pdf_source TEXT NOT NULL,
            ref_number TEXT,
            authors TEXT NOT NULL,
            title TEXT NOT NULL,
            year TEXT,
            journal TEXT,
            volume TEXT,
            issue TEXT,
            pages TEXT,
            doi TEXT,
            url TEXT,
            abstract TEXT,
            keywords TEXT,
            citation_type TEXT DEFAULT 'article',
            confidence_score REAL DEFAULT 0.0,
            verified BOOLEAN DEFAULT 0,
            notes TEXT,
            tags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_title ON "references"(title);
        CREATE INDEX IF NOT EXISTS idx_authors ON "references"(authors);
        CREATE INDEX IF NOT EXISTS idx_year ON "references"(year);
        CREATE INDEX IF NOT EXISTS idx_doi ON "references"(doi);
        CREATE INDEX IF NOT EXISTS idx_pdf_source ON "references"(pdf_source);
        CREATE INDEX IF NOT EXISTS idx_confidence ON "references"(confidence_score);

        CREATE TABLE IF NOT EXISTS processing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pdf_file TEXT NOT NULL,
            references_found INTEGER DEFAULT 0,
            processing_time REAL DEFAULT 0.0,
            status TEXT DEFAULT 'pending',
            error_message TEXT,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_pdf_file ON processing_history(pdf_file);

        CREATE TABLE IF NOT EXISTS export_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            export_format TEXT NOT NULL,
            output_file TEXT NOT NULL,
            reference_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#3498db',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value TEXT NOT NULL,
            recorded_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_metric_name ON statistics(metric_name);
        """

        try:
            with self.get_connection() as conn:
                conn.executescript(schema)
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def add_reference(self, ref: Reference) -> Optional[int]:
        """
        Add a new reference to the database

        Args:
            ref: Reference object

        Returns:
            Reference ID if successful, None otherwise
        """
        try:
            now = datetime.now().isoformat()
            ref.created_at = now
            ref.updated_at = now

            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO "references" (
                        pdf_source, ref_number, authors, title, year, journal,
                        volume, issue, pages, doi, url, abstract, keywords,
                        citation_type, confidence_score, verified, notes, tags,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ref.pdf_source, ref.ref_number, ref.authors, ref.title, ref.year,
                    ref.journal, ref.volume, ref.issue, ref.pages, ref.doi, ref.url,
                    ref.abstract, ref.keywords, ref.citation_type, ref.confidence_score,
                    ref.verified, ref.notes, ref.tags, ref.created_at, ref.updated_at
                ))
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to add reference: {e}")
            return None

    def bulk_add_references(self, refs: List[Reference]) -> int:
        """
        Add multiple references in a single transaction

        Args:
            refs: List of Reference objects

        Returns:
            Number of successfully added references
        """
        count = 0
        try:
            now = datetime.now().isoformat()
            with self.get_connection() as conn:
                for ref in refs:
                    ref.created_at = now
                    ref.updated_at = now
                    conn.execute("""
                        INSERT INTO "references" (
                            pdf_source, ref_number, authors, title, year, journal,
                            volume, issue, pages, doi, url, abstract, keywords,
                            citation_type, confidence_score, verified, notes, tags,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ref.pdf_source, ref.ref_number, ref.authors, ref.title, ref.year,
                        ref.journal, ref.volume, ref.issue, ref.pages, ref.doi, ref.url,
                        ref.abstract, ref.keywords, ref.citation_type, ref.confidence_score,
                        ref.verified, ref.notes, ref.tags, ref.created_at, ref.updated_at
                    ))
                    count += 1
            self.logger.info(f"Bulk added {count} references")
        except Exception as e:
            self.logger.error(f"Failed to bulk add references: {e}")
        return count

    def get_reference(self, ref_id: int) -> Optional[Reference]:
        """Get reference by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM \"references\" WHERE id = ?", (ref_id,))
                row = cursor.fetchone()
                if row:
                    return Reference(**dict(row))
        except Exception as e:
            self.logger.error(f"Failed to get reference: {e}")
        return None

    def get_all_references(self, limit: Optional[int] = None, offset: int = 0) -> List[Reference]:
        """
        Get all references with pagination

        Args:
            limit: Maximum number of results
            offset: Starting position

        Returns:
            List of Reference objects
        """
        try:
            query = "SELECT * FROM \"references\" ORDER BY created_at DESC"
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"

            with self.get_connection() as conn:
                cursor = conn.execute(query)
                return [Reference(**dict(row)) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get all references: {e}")
            return []

    def search_references(self, query: str, fields: List[str] = None) -> List[Reference]:
        """
        Search references across multiple fields

        Args:
            query: Search query
            fields: Fields to search in (default: title, authors, journal)

        Returns:
            List of matching Reference objects
        """
        if not fields:
            fields = ['title', 'authors', 'journal']

        try:
            conditions = " OR ".join([f"{field} LIKE ?" for field in fields])
            sql = f"SELECT * FROM \"references\" WHERE {conditions} ORDER BY confidence_score DESC"
            params = [f"%{query}%" for _ in fields]

            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                return [Reference(**dict(row)) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to search references: {e}")
            return []

    def update_reference(self, ref_id: int, **kwargs) -> bool:
        """
        Update reference fields

        Args:
            ref_id: Reference ID
            **kwargs: Fields to update

        Returns:
            True if successful
        """
        try:
            kwargs['updated_at'] = datetime.now().isoformat()
            set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values()) + [ref_id]

            with self.get_connection() as conn:
                conn.execute(f"UPDATE \"references\" SET {set_clause} WHERE id = ?", values)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update reference: {e}")
            return False

    def delete_reference(self, ref_id: int) -> bool:
        """Delete reference by ID"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM \"references\" WHERE id = ?", (ref_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete reference: {e}")
            return False

    def get_references_by_pdf(self, pdf_source: str) -> List[Reference]:
        """Get all references from a specific PDF"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM \"references\" WHERE pdf_source = ? ORDER BY ref_number",
                    (pdf_source,)
                )
                return [Reference(**dict(row)) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get references by PDF: {e}")
            return []

    def add_processing_history(self, pdf_file: str, refs_found: int,
                               processing_time: float, status: str = "success",
                               error_msg: str = "") -> Optional[int]:
        """Record processing history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO processing_history
                    (pdf_file, references_found, processing_time, status, error_message, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (pdf_file, refs_found, processing_time, status, error_msg,
                      datetime.now().isoformat()))
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Failed to add processing history: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                stats = {}

                # Total references
                cursor = conn.execute("SELECT COUNT(*) FROM \"references\"")
                stats['total_references'] = cursor.fetchone()[0]

                # By year
                cursor = conn.execute("""
                    SELECT year, COUNT(*) as count
                    FROM "references"
                    WHERE year != ''
                    GROUP BY year
                    ORDER BY year DESC
                    LIMIT 10
                """)
                stats['by_year'] = dict(cursor.fetchall())

                # By citation type
                cursor = conn.execute("""
                    SELECT citation_type, COUNT(*) as count
                    FROM "references"
                    GROUP BY citation_type
                """)
                stats['by_type'] = dict(cursor.fetchall())

                # Average confidence score
                cursor = conn.execute("SELECT AVG(confidence_score) FROM \"references\"")
                stats['avg_confidence'] = cursor.fetchone()[0] or 0.0

                # Total PDFs processed
                cursor = conn.execute("SELECT COUNT(DISTINCT pdf_source) FROM \"references\"")
                stats['total_pdfs'] = cursor.fetchone()[0]

                return stats
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}

    def clear_all_references(self) -> bool:
        """Clear all references (use with caution)"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM \"references\"")
            self.logger.warning("All references cleared from database")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear references: {e}")
            return False

    def export_to_json(self, output_path: Path) -> bool:
        """Export all references to JSON"""
        try:
            refs = self.get_all_references()
            data = [ref.to_dict() for ref in refs]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Exported {len(refs)} references to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {e}")
            return False

    def import_from_json(self, input_path: Path) -> int:
        """Import references from JSON"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            refs = [Reference.from_dict(item) for item in data]
            count = self.bulk_add_references(refs)
            self.logger.info(f"Imported {count} references from {input_path}")
            return count
        except Exception as e:
            self.logger.error(f"Failed to import from JSON: {e}")
            return 0
