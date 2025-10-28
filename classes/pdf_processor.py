"""
Advanced PDF Processor with ML-Enhanced Extraction
Enterprise-level PDF processing with layout analysis and confidence scoring
"""

import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any
import fitz  # PyMuPDF
from dataclasses import dataclass


@dataclass
class TextBlock:
    """Represents a text block from PDF"""
    text: str
    x: float
    y: float
    width: float
    height: float
    font_size: float
    font_name: str
    page_num: int
    confidence: float = 1.0


@dataclass
class PDFMetadata:
    """PDF document metadata"""
    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: str = ""
    mod_date: str = ""
    page_count: int = 0
    file_size: int = 0


class PDFProcessor:
    """
    Advanced PDF processor with intelligent text extraction
    """

    def __init__(self, enable_ml: bool = True, enable_ocr: bool = False):
        self.logger = logging.getLogger(__name__)
        self.enable_ml = enable_ml
        self.enable_ocr = enable_ocr

    def extract_metadata(self, pdf_path: Path) -> PDFMetadata:
        """
        Extract PDF metadata

        Args:
            pdf_path: Path to PDF file

        Returns:
            PDFMetadata object
        """
        try:
            doc = fitz.open(str(pdf_path))
            metadata = doc.metadata or {}

            pdf_meta = PDFMetadata(
                title=metadata.get('title', ''),
                author=metadata.get('author', ''),
                subject=metadata.get('subject', ''),
                keywords=metadata.get('keywords', ''),
                creator=metadata.get('creator', ''),
                producer=metadata.get('producer', ''),
                creation_date=metadata.get('creationDate', ''),
                mod_date=metadata.get('modDate', ''),
                page_count=doc.page_count,
                file_size=pdf_path.stat().st_size
            )

            doc.close()
            self.logger.debug(f"Extracted metadata from {pdf_path.name}")
            return pdf_meta
        except Exception as e:
            self.logger.error(f"Failed to extract metadata: {e}")
            return PDFMetadata()

    def extract_text_blocks(self, pdf_path: Path) -> List[TextBlock]:
        """
        Extract text blocks with positioning information

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of TextBlock objects
        """
        blocks = []
        try:
            doc = fitz.open(str(pdf_path))

            for page_num, page in enumerate(doc):
                raw_blocks = page.get_text("dict")["blocks"]

                for block in raw_blocks:
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            text_parts = []
                            avg_font_size = 0
                            font_names = []

                            for span in line.get("spans", []):
                                text_parts.append(span["text"])
                                avg_font_size += span["size"]
                                font_names.append(span["font"])

                            if text_parts:
                                text = " ".join(text_parts)
                                avg_font_size /= len(line["spans"])

                                blocks.append(TextBlock(
                                    text=text,
                                    x=block["bbox"][0],
                                    y=block["bbox"][1],
                                    width=block["bbox"][2] - block["bbox"][0],
                                    height=block["bbox"][3] - block["bbox"][1],
                                    font_size=avg_font_size,
                                    font_name=font_names[0] if font_names else "",
                                    page_num=page_num + 1
                                ))

            doc.close()
            self.logger.info(f"Extracted {len(blocks)} text blocks from {pdf_path.name}")
        except Exception as e:
            self.logger.error(f"Failed to extract text blocks: {e}")

        return blocks

    def extract_text_columnar(self, pdf_path: Path) -> str:
        """
        Extract text with column awareness (for multi-column papers)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        try:
            doc = fitz.open(str(pdf_path))
            full_text = []

            for page_num, page in enumerate(doc):
                blocks = page.get_text("blocks")
                if not blocks:
                    continue

                # Detect columns
                width = page.rect.width
                midpoint = width / 2

                # Separate left and right column blocks
                left_blocks = [b for b in blocks if b[0] < midpoint]
                right_blocks = [b for b in blocks if b[0] >= midpoint]

                # Sort by vertical position
                left_blocks.sort(key=lambda b: b[1])
                right_blocks.sort(key=lambda b: b[1])

                # Combine in reading order
                combined = left_blocks + right_blocks
                page_text = "\n".join(b[4].strip() for b in combined if b[4].strip())
                full_text.append(page_text)

                # Log if REFERENCES section found
                if 'REFERENCES' in page_text.upper():
                    self.logger.debug(f"Found REFERENCES on page {page_num + 1}")

            doc.close()
            return "\n".join(full_text)
        except Exception as e:
            self.logger.error(f"Failed to extract columnar text: {e}")
            return ""

    def detect_references_section(self, text: str) -> Tuple[int, int]:
        """
        Detect the start and end positions of references section

        Args:
            text: Full document text

        Returns:
            Tuple of (start_pos, end_pos)
        """
        # Try multiple patterns
        patterns = [
            r'\bREFERENCES\b',
            r'\bREFERENCE\b',
            r'\bBIBLIOGRAPHY\b',
            r'\bWORKS CITED\b'
        ]

        start_pos = -1
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_pos = match.end()
                self.logger.info(f"Found references section at position {start_pos}")
                break

        if start_pos == -1:
            self.logger.warning("No references section found")
            return (-1, -1)

        # Try to find end of references (next section)
        end_patterns = [
            r'\bAPPENDIX\b',
            r'\bACKNOWLEDGMENT\b',
            r'\bACKNOWLEDGEMENT\b'
        ]

        end_pos = len(text)
        for pattern in end_patterns:
            match = re.search(pattern, text[start_pos:], re.IGNORECASE)
            if match:
                end_pos = start_pos + match.start()
                break

        return (start_pos, end_pos)

    def extract_references_section(self, pdf_path: Path) -> str:
        """
        Extract only the references section from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            References section text
        """
        text = self.extract_text_columnar(pdf_path)
        start, end = self.detect_references_section(text)

        if start == -1:
            return ""

        refs_text = text[start:end]

        # Clean up
        refs_text = re.sub(r'[\x00-\x1F\x7F\u00AD]', '', refs_text)
        refs_text = refs_text.strip()

        self.logger.info(f"Extracted {len(refs_text)} characters from references section")
        return refs_text

    def analyze_document_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Analyze document structure and layout

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with structure analysis
        """
        analysis = {
            'has_multiple_columns': False,
            'avg_font_size': 0.0,
            'page_count': 0,
            'total_blocks': 0,
            'references_page': -1,
            'references_found': False
        }

        try:
            doc = fitz.open(str(pdf_path))
            analysis['page_count'] = doc.page_count

            all_font_sizes = []
            total_blocks = 0

            for page_num, page in enumerate(doc):
                blocks = page.get_text("dict")["blocks"]
                total_blocks += len(blocks)

                # Check for references
                page_text = page.get_text()
                if 'REFERENCES' in page_text.upper() and analysis['references_page'] == -1:
                    analysis['references_page'] = page_num + 1
                    analysis['references_found'] = True

                # Analyze font sizes
                for block in blocks:
                    if block.get("type") == 0:
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                all_font_sizes.append(span["size"])

                # Check for multiple columns (simple heuristic)
                if len(blocks) > 10:
                    x_positions = [b["bbox"][0] for b in blocks if b.get("type") == 0]
                    if x_positions:
                        unique_x = len(set(round(x / 10) * 10 for x in x_positions))
                        if unique_x > 2:
                            analysis['has_multiple_columns'] = True

            analysis['total_blocks'] = total_blocks
            if all_font_sizes:
                analysis['avg_font_size'] = sum(all_font_sizes) / len(all_font_sizes)

            doc.close()
            self.logger.info(f"Document analysis complete: {analysis}")
        except Exception as e:
            self.logger.error(f"Failed to analyze document structure: {e}")

        return analysis

    def extract_images(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """
        Extract images from PDF

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images

        Returns:
            List of saved image paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_images = []

        try:
            doc = fitz.open(str(pdf_path))

            for page_num, page in enumerate(doc):
                image_list = page.get_images()

                for img_idx, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    image_path = output_dir / f"{pdf_path.stem}_p{page_num + 1}_img{img_idx + 1}.{image_ext}"
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    saved_images.append(image_path)

            doc.close()
            self.logger.info(f"Extracted {len(saved_images)} images from {pdf_path.name}")
        except Exception as e:
            self.logger.error(f"Failed to extract images: {e}")

        return saved_images

    def calculate_confidence_score(self, text: str) -> float:
        """
        Calculate confidence score for extracted text

        Args:
            text: Extracted text

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not text:
            return 0.0

        score = 1.0

        # Check for garbled text
        garbled_chars = len(re.findall(r'[^\w\s\.,;:\-\(\)\[\]{}]', text))
        garbled_ratio = garbled_chars / len(text)
        if garbled_ratio > 0.1:
            score -= 0.3

        # Check for proper spacing
        no_space_ratio = len(re.findall(r'[a-z][A-Z]', text)) / max(len(text), 1)
        if no_space_ratio > 0.05:
            score -= 0.2

        # Check for numeric patterns (common in references)
        has_years = bool(re.search(r'\b(19|20)\d{2}\b', text))
        has_numbers = bool(re.search(r'\[\d+\]', text))
        if has_years and has_numbers:
            score += 0.1

        # Check text length
        if len(text) < 50:
            score -= 0.2

        return max(0.0, min(1.0, score))

    def validate_pdf(self, pdf_path: Path) -> Tuple[bool, str]:
        """
        Validate PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not pdf_path.exists():
            return (False, "File does not exist")

        if pdf_path.suffix.lower() != '.pdf':
            return (False, "Not a PDF file")

        if pdf_path.stat().st_size == 0:
            return (False, "File is empty")

        try:
            doc = fitz.open(str(pdf_path))
            if doc.page_count == 0:
                doc.close()
                return (False, "PDF has no pages")
            doc.close()
            return (True, "")
        except Exception as e:
            return (False, f"Corrupted PDF: {str(e)}")

    def batch_process(self, pdf_paths: List[Path]) -> Dict[Path, str]:
        """
        Process multiple PDFs and extract references

        Args:
            pdf_paths: List of PDF paths

        Returns:
            Dictionary mapping paths to extracted references
        """
        results = {}

        for pdf_path in pdf_paths:
            try:
                is_valid, error = self.validate_pdf(pdf_path)
                if not is_valid:
                    self.logger.error(f"Invalid PDF {pdf_path.name}: {error}")
                    results[pdf_path] = ""
                    continue

                refs_text = self.extract_references_section(pdf_path)
                results[pdf_path] = refs_text
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_path.name}: {e}")
                results[pdf_path] = ""

        return results
