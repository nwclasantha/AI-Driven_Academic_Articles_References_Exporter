"""
Advanced Reference Parser with ML-Enhanced Extraction
Supports multiple citation styles and confidence scoring
"""

import re
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from difflib import SequenceMatcher


@dataclass
class ParsedReference:
    """Structured reference data"""
    raw_text: str
    ref_number: str = ""
    authors: List[str] = field(default_factory=list)
    title: str = ""
    year: str = ""
    journal: str = ""
    booktitle: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""
    doi: str = ""
    url: str = ""
    isbn: str = ""
    issn: str = ""
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    citation_type: str = "article"  # article, inproceedings, book, etc.
    confidence: float = 0.0
    parsing_notes: List[str] = field(default_factory=list)

    def get_author_string(self) -> str:
        """Get formatted author string"""
        if not self.authors:
            return ""
        if len(self.authors) == 1:
            return self.authors[0]
        return " and ".join(self.authors)


class ReferenceParser:
    """
    Advanced reference parser with pattern matching and ML features
    """

    def __init__(self, style: str = "ieee"):
        self.logger = logging.getLogger(__name__)
        self.style = style.lower()

        # Quote characters (ASCII and Unicode)
        self.quote_pairs = [
            ('"', '"'),                    # ASCII double
            (chr(8220), chr(8221)),        # Unicode left/right double
            ("'", "'"),                    # ASCII single
            (chr(8216), chr(8217))         # Unicode left/right single
        ]

    def parse_references_section(self, text: str) -> List[ParsedReference]:
        """
        Parse references section into structured data

        Args:
            text: References section text

        Returns:
            List of ParsedReference objects
        """
        # Clean text
        text = self._clean_text(text)

        # Split into individual references
        raw_refs = self._split_references(text)
        self.logger.info(f"Found {len(raw_refs)} raw reference entries")

        # Parse each reference
        parsed = []
        for i, raw_ref in enumerate(raw_refs):
            try:
                ref = self._parse_single_reference(raw_ref, i + 1)
                if ref:
                    parsed.append(ref)
            except Exception as e:
                self.logger.error(f"Failed to parse reference {i + 1}: {e}")

        # Remove duplicates
        parsed = self._remove_duplicates(parsed)
        self.logger.info(f"Parsed {len(parsed)} unique references")

        return parsed

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove control characters
        text = re.sub(r'[\x00-\x1F\x7F\u00AD]', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Normalize dashes
        text = text.replace('–', '-').replace('—', '-')

        return text.strip()

    def _split_references(self, text: str) -> List[str]:
        """
        Split text into individual reference entries

        Args:
            text: References section text

        Returns:
            List of raw reference strings
        """
        # Try numbered references [1], [2], etc.
        numbered = re.findall(r'\[\d+\]\s*(.*?)(?=\[\d+\]|\Z)', text, re.DOTALL)
        if numbered:
            return [ref.strip() for ref in numbered if ref.strip()]

        # Try numbered without brackets: 1., 2., etc.
        numbered_dots = re.split(r'\n\s*\d+\.\s+', text)
        if len(numbered_dots) > 5:
            return [ref.strip() for ref in numbered_dots if ref.strip()]

        # Try author-year style splits
        author_year = re.split(r'\n\s*(?=[A-Z][a-z]+,\s+[A-Z])', text)
        if len(author_year) > 5:
            return [ref.strip() for ref in author_year if ref.strip()]

        # Fallback: split by newlines with heuristics
        lines = text.split('\n')
        refs = []
        current_ref = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Start of new reference heuristic
            if (re.match(r'^\[\d+\]', line) or
                re.match(r'^\d+\.', line) or
                (re.match(r'^[A-Z][a-z]+,', line) and current_ref)):

                if current_ref:
                    refs.append(' '.join(current_ref))
                current_ref = [line]
            else:
                current_ref.append(line)

        if current_ref:
            refs.append(' '.join(current_ref))

        return refs

    def _parse_single_reference(self, text: str, ref_num: int) -> Optional[ParsedReference]:
        """
        Parse a single reference entry

        Args:
            text: Reference text
            ref_num: Reference number

        Returns:
            ParsedReference object or None
        """
        if not text or len(text) < 10:
            return None

        ref = ParsedReference(raw_text=text, ref_number=str(ref_num))

        # Extract reference number if present
        num_match = re.match(r'^\[(\d+)\]', text)
        if num_match:
            ref.ref_number = num_match.group(1)
            text = text[num_match.end():].strip()

        # Extract DOI
        doi_match = re.search(r'(?:doi:|DOI:)?\s*(10\.\d{4,}/[^\s]+)', text, re.IGNORECASE)
        if doi_match:
            ref.doi = doi_match.group(1).rstrip('.,;')
            ref.confidence += 0.15

        # Extract URL
        url_match = re.search(r'(https?://[^\s]+)', text)
        if url_match:
            ref.url = url_match.group(1).rstrip('.,;')
            ref.confidence += 0.05

        # Extract title (quoted text)
        title = self._extract_quoted_text(text)
        if title:
            ref.title = title
            ref.confidence += 0.25
        else:
            ref.title = "Untitled"
            ref.parsing_notes.append("No quoted title found")

        # Extract year
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            ref.year = year_match.group(0)
            ref.confidence += 0.15
        else:
            ref.parsing_notes.append("No year found")

        # Extract authors (before title)
        authors = self._extract_authors(text, ref.title)
        if authors:
            ref.authors = authors
            ref.confidence += 0.20
        else:
            ref.parsing_notes.append("No authors found")

        # Extract journal/venue info (after title)
        journal_info = self._extract_journal_info(text, ref.title)
        ref.journal = journal_info.get('journal', '')
        ref.booktitle = journal_info.get('booktitle', '')
        ref.publisher = journal_info.get('publisher', '')

        # Determine citation type
        ref.citation_type = self._determine_citation_type(text, journal_info)

        # Extract volume, issue, pages
        ref.volume = self._extract_volume(text)
        ref.issue = self._extract_issue(text)
        ref.pages = self._extract_pages(text)

        if ref.volume:
            ref.confidence += 0.10
        if ref.pages:
            ref.confidence += 0.10

        # Normalize confidence
        ref.confidence = min(1.0, ref.confidence)

        return ref

    def _extract_quoted_text(self, text: str) -> str:
        """Extract text within quotes"""
        for open_q, close_q in self.quote_pairs:
            pattern = f'{re.escape(open_q)}([^{re.escape(close_q)}]+){re.escape(close_q)}'
            match = re.search(pattern, text)
            if match:
                return self._clean_field(match.group(1))
        return ""

    def _extract_authors(self, text: str, title: str) -> List[str]:
        """
        Extract author names from text

        Args:
            text: Reference text
            title: Extracted title (to know where authors end)

        Returns:
            List of author names
        """
        # Find text before title
        author_part = text
        if title:
            for open_q, _ in self.quote_pairs:
                if open_q in text:
                    author_part = text.split(open_q)[0]
                    break

        author_part = author_part.strip(' ,:;')

        # Remove reference number
        author_part = re.sub(r'^\[\d+\]\s*', '', author_part)

        # Clean up
        author_part = self._clean_field(author_part)

        if not author_part:
            return []

        # Split by 'and' or commas
        authors = []

        # Try "and" separator
        if ' and ' in author_part.lower():
            parts = re.split(r'\s+and\s+', author_part, flags=re.IGNORECASE)
            authors = [self._clean_field(p) for p in parts if p.strip()]
        else:
            # Try comma separation (careful not to split middle names)
            parts = author_part.split(',')
            # Simple heuristic: if parts look like "LastName, FirstName" pairs
            if len(parts) >= 2:
                authors = [self._clean_field(p) for p in parts if p.strip()]
            else:
                authors = [author_part]

        return [a for a in authors if a and len(a) > 2]

    def _extract_journal_info(self, text: str, title: str) -> Dict[str, str]:
        """Extract journal/venue information"""
        info = {'journal': '', 'booktitle': '', 'publisher': ''}

        # Find text after title
        post_title = text
        if title:
            for _, close_q in self.quote_pairs:
                if close_q in text:
                    close_pos = text.rfind(close_q)
                    if close_pos != -1:
                        post_title = text[close_pos + 1:].strip(' ,:;')
                        break

        # Remove year, volume, issue, pages to isolate venue
        post_title = re.sub(r'\b(19|20)\d{2}\b', '', post_title)
        post_title = re.sub(r'vol\.\s*\d+', '', post_title, flags=re.IGNORECASE)
        post_title = re.sub(r'no\.\s*\d+', '', post_title, flags=re.IGNORECASE)
        post_title = re.sub(r'pp\.\s*[\d\-]+', '', post_title, flags=re.IGNORECASE)
        post_title = self._clean_field(post_title)

        # Detect if conference or journal
        conf_keywords = ['conference', 'proc', 'proceedings', 'symposium', 'workshop', 'congress']
        is_conf = any(kw in post_title.lower() for kw in conf_keywords)

        if is_conf:
            info['booktitle'] = post_title
        else:
            info['journal'] = post_title

        return info

    def _determine_citation_type(self, text: str, journal_info: Dict[str, str]) -> str:
        """Determine BibTeX citation type"""
        text_lower = text.lower()

        if journal_info.get('booktitle'):
            return 'inproceedings'

        if any(kw in text_lower for kw in ['conference', 'proc', 'symposium', 'workshop']):
            return 'inproceedings'

        if any(kw in text_lower for kw in ['book', 'edition', 'isbn']):
            return 'book'

        if any(kw in text_lower for kw in ['thesis', 'dissertation']):
            return 'phdthesis'

        if 'technical report' in text_lower or 'tech. rep' in text_lower:
            return 'techreport'

        return 'article'

    def _extract_volume(self, text: str) -> str:
        """Extract volume number"""
        patterns = [
            r'vol\.\s*(\d+)',
            r'volume\s+(\d+)',
            r'\bv\.\s*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _extract_issue(self, text: str) -> str:
        """Extract issue/number"""
        patterns = [
            r'no\.\s*(\d+)',
            r'number\s+(\d+)',
            r'issue\s+(\d+)',
            r'\bn\.\s*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""

    def _extract_pages(self, text: str) -> str:
        """Extract page numbers"""
        patterns = [
            r'pp\.\s*([\d\-]+)',
            r'pages?\s+([\d\-]+)',
            r',\s*([\d]+)\s*[-–—]\s*([\d]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) > 1:
                    return f"{match.group(1)}-{match.group(2)}"
                return match.group(1).replace('–', '-').replace('—', '-')
        return ""

    def _clean_field(self, text: str) -> str:
        """Clean a field value"""
        # Remove trailing punctuation
        text = re.sub(r'[.,;:]+$', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _remove_duplicates(self, refs: List[ParsedReference]) -> List[ParsedReference]:
        """
        Remove duplicate references based on title similarity

        Args:
            refs: List of references

        Returns:
            Deduplicated list
        """
        unique = []

        for ref in refs:
            is_duplicate = False
            for existing in unique:
                similarity = self._calculate_similarity(ref.title, existing.title)
                if similarity > 0.85:
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if ref.confidence > existing.confidence:
                        unique.remove(existing)
                        unique.append(ref)
                    break

            if not is_duplicate:
                unique.append(ref)

        removed = len(refs) - len(unique)
        if removed > 0:
            self.logger.info(f"Removed {removed} duplicate references")

        return unique

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not str1 or not str2:
            return 0.0

        # Normalize
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()

        # Use SequenceMatcher for character-level similarity
        char_sim = SequenceMatcher(None, s1, s2).ratio()

        # Use word-level Jaccard similarity
        words1 = set(s1.split())
        words2 = set(s2.split())
        if words1 and words2:
            word_sim = len(words1 & words2) / len(words1 | words2)
        else:
            word_sim = 0.0

        # Combined score
        return (char_sim + word_sim) / 2

    def validate_reference(self, ref: ParsedReference) -> Tuple[bool, List[str]]:
        """
        Validate a parsed reference

        Args:
            ref: ParsedReference object

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        if not ref.title or ref.title == "Untitled":
            errors.append("Missing title")

        if not ref.authors:
            errors.append("Missing authors")

        if not ref.year:
            errors.append("Missing year")
        elif not re.match(r'^(19|20)\d{2}$', ref.year):
            errors.append("Invalid year format")

        if ref.confidence < 0.3:
            errors.append("Low confidence score")

        return (len(errors) == 0, errors)

    def get_statistics(self, refs: List[ParsedReference]) -> Dict[str, Any]:
        """Get parsing statistics"""
        if not refs:
            return {}

        return {
            'total': len(refs),
            'avg_confidence': sum(r.confidence for r in refs) / len(refs),
            'with_doi': sum(1 for r in refs if r.doi),
            'with_url': sum(1 for r in refs if r.url),
            'by_type': self._count_by_type(refs),
            'by_year': self._count_by_year(refs),
            'low_confidence': sum(1 for r in refs if r.confidence < 0.5)
        }

    def _count_by_type(self, refs: List[ParsedReference]) -> Dict[str, int]:
        """Count references by type"""
        counts = {}
        for ref in refs:
            counts[ref.citation_type] = counts.get(ref.citation_type, 0) + 1
        return counts

    def _count_by_year(self, refs: List[ParsedReference]) -> Dict[str, int]:
        """Count references by year"""
        counts = {}
        for ref in refs:
            if ref.year:
                counts[ref.year] = counts.get(ref.year, 0) + 1
        return counts
