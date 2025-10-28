"""
API Integration Layer
Enterprise-level API clients for CrossRef, DOI, and metadata enrichment
"""

import logging
import time
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import urllib.parse


@dataclass
class APIResult:
    """API call result"""
    success: bool
    data: Dict[str, Any]
    error: str = ""
    source: str = ""


class RateLimiter:
    """
    Simple rate limiter for API calls
    """

    def __init__(self, max_calls: int = 5, period: float = 1.0):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()

        # Remove old calls outside the period
        self.calls = [c for c in self.calls if now - c < self.period]

        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.calls.append(time.time())


class CrossRefClient:
    """
    Client for CrossRef API
    https://www.crossref.org/documentation/retrieve-metadata/rest-api/
    """

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, rate_limit: int = 5, timeout: int = 10):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.rate_limiter = RateLimiter(max_calls=rate_limit, period=1.0)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'IEEE-Reference-Extractor/3.0 (mailto:research@example.com)'
        })

    def lookup_by_doi(self, doi: str) -> APIResult:
        """
        Look up reference by DOI

        Args:
            doi: DOI string

        Returns:
            APIResult object
        """
        try:
            self.rate_limiter.wait_if_needed()

            url = f"{self.BASE_URL}/{doi}"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})

                result = {
                    'title': self._extract_title(message),
                    'authors': self._extract_authors(message),
                    'year': self._extract_year(message),
                    'journal': message.get('container-title', [''])[0],
                    'volume': message.get('volume', ''),
                    'issue': message.get('issue', ''),
                    'pages': message.get('page', ''),
                    'doi': doi,
                    'url': message.get('URL', ''),
                    'publisher': message.get('publisher', ''),
                    'issn': ', '.join(message.get('ISSN', [])),
                    'type': message.get('type', 'article')
                }

                self.logger.info(f"CrossRef lookup successful for DOI: {doi}")
                return APIResult(success=True, data=result, source='crossref')
            else:
                self.logger.warning(f"CrossRef lookup failed: {response.status_code}")
                return APIResult(success=False, data={}, error=f"Status {response.status_code}", source='crossref')

        except Exception as e:
            self.logger.error(f"CrossRef lookup error: {e}")
            return APIResult(success=False, data={}, error=str(e), source='crossref')

    def search_by_title(self, title: str, limit: int = 5) -> List[APIResult]:
        """
        Search for references by title

        Args:
            title: Title to search
            limit: Maximum results

        Returns:
            List of APIResult objects
        """
        try:
            self.rate_limiter.wait_if_needed()

            params = {
                'query.title': title,
                'rows': limit
            }

            response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                items = data.get('message', {}).get('items', [])

                results = []
                for item in items:
                    result = {
                        'title': self._extract_title(item),
                        'authors': self._extract_authors(item),
                        'year': self._extract_year(item),
                        'journal': item.get('container-title', [''])[0],
                        'volume': item.get('volume', ''),
                        'issue': item.get('issue', ''),
                        'pages': item.get('page', ''),
                        'doi': item.get('DOI', ''),
                        'url': item.get('URL', ''),
                        'publisher': item.get('publisher', ''),
                        'issn': ', '.join(item.get('ISSN', [])),
                        'type': item.get('type', 'article')
                    }
                    results.append(APIResult(success=True, data=result, source='crossref'))

                self.logger.info(f"CrossRef search found {len(results)} results for: {title}")
                return results
            else:
                self.logger.warning(f"CrossRef search failed: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"CrossRef search error: {e}")
            return []

    def _extract_title(self, item: Dict) -> str:
        """Extract title from CrossRef item"""
        titles = item.get('title', [])
        return titles[0] if titles else ''

    def _extract_authors(self, item: Dict) -> List[str]:
        """Extract authors from CrossRef item"""
        authors = []
        for author in item.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            if given and family:
                authors.append(f"{given} {family}")
            elif family:
                authors.append(family)
        return authors

    def _extract_year(self, item: Dict) -> str:
        """Extract year from CrossRef item"""
        date_parts = item.get('published-print', {}).get('date-parts', [])
        if not date_parts:
            date_parts = item.get('published-online', {}).get('date-parts', [])
        if date_parts and date_parts[0]:
            return str(date_parts[0][0])
        return ''


class DOIClient:
    """
    Client for DOI.org resolution
    """

    BASE_URL = "https://doi.org"

    def __init__(self, timeout: int = 10):
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout
        self.session = requests.Session()

    def resolve_doi(self, doi: str) -> APIResult:
        """
        Resolve DOI to metadata

        Args:
            doi: DOI string

        Returns:
            APIResult object
        """
        try:
            url = f"{self.BASE_URL}/{doi}"
            headers = {'Accept': 'application/vnd.citationstyles.csl+json'}

            response = self.session.get(url, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()

                result = {
                    'title': data.get('title', ''),
                    'authors': self._extract_authors(data),
                    'year': self._extract_year(data),
                    'journal': data.get('container-title', ''),
                    'volume': data.get('volume', ''),
                    'issue': data.get('issue', ''),
                    'pages': data.get('page', ''),
                    'doi': doi,
                    'url': data.get('URL', ''),
                    'publisher': data.get('publisher', ''),
                    'issn': data.get('ISSN', ''),
                    'type': data.get('type', 'article')
                }

                self.logger.info(f"DOI resolution successful: {doi}")
                return APIResult(success=True, data=result, source='doi.org')
            else:
                self.logger.warning(f"DOI resolution failed: {response.status_code}")
                return APIResult(success=False, data={}, error=f"Status {response.status_code}", source='doi.org')

        except Exception as e:
            self.logger.error(f"DOI resolution error: {e}")
            return APIResult(success=False, data={}, error=str(e), source='doi.org')

    def _extract_authors(self, data: Dict) -> List[str]:
        """Extract authors from DOI metadata"""
        authors = []
        for author in data.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            if given and family:
                authors.append(f"{given} {family}")
            elif family:
                authors.append(family)
        return authors

    def _extract_year(self, data: Dict) -> str:
        """Extract year from DOI metadata"""
        issued = data.get('issued', {})
        date_parts = issued.get('date-parts', [])
        if date_parts and date_parts[0]:
            return str(date_parts[0][0])
        return ''


class MetadataEnricher:
    """
    Enriches reference metadata using multiple API sources
    """

    def __init__(self, enable_crossref: bool = True, enable_doi: bool = True):
        self.logger = logging.getLogger(__name__)
        self.crossref = CrossRefClient() if enable_crossref else None
        self.doi_client = DOIClient() if enable_doi else None

    def enrich_reference(self, ref_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich reference with additional metadata

        Args:
            ref_data: Partial reference data

        Returns:
            Enriched reference data
        """
        enriched = ref_data.copy()

        # Try DOI lookup first if DOI is available
        if ref_data.get('doi') and self.doi_client:
            self.logger.info(f"Enriching via DOI: {ref_data['doi']}")
            result = self.doi_client.resolve_doi(ref_data['doi'])
            if result.success:
                enriched = self._merge_metadata(enriched, result.data)
                enriched['enriched_by'] = 'doi.org'
                return enriched

        # Try CrossRef DOI lookup
        if ref_data.get('doi') and self.crossref:
            result = self.crossref.lookup_by_doi(ref_data['doi'])
            if result.success:
                enriched = self._merge_metadata(enriched, result.data)
                enriched['enriched_by'] = 'crossref'
                return enriched

        # Try CrossRef title search
        if ref_data.get('title') and self.crossref:
            self.logger.info(f"Enriching via title search: {ref_data['title'][:50]}")
            results = self.crossref.search_by_title(ref_data['title'], limit=3)
            if results:
                # Use the best match (first result)
                enriched = self._merge_metadata(enriched, results[0].data)
                enriched['enriched_by'] = 'crossref_search'
                return enriched

        self.logger.info("No enrichment sources available")
        return enriched

    def _merge_metadata(self, original: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge metadata, preferring non-empty values from new data

        Args:
            original: Original metadata
            new: New metadata

        Returns:
            Merged metadata
        """
        merged = original.copy()

        for key, value in new.items():
            if value:  # Only use non-empty values
                if key not in merged or not merged[key]:
                    merged[key] = value
                elif isinstance(value, list) and isinstance(merged[key], list):
                    # Merge lists
                    merged[key] = list(set(merged[key] + value))

        return merged

    def batch_enrich(self, references: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich multiple references

        Args:
            references: List of reference data

        Returns:
            List of enriched references
        """
        enriched = []
        total = len(references)

        for i, ref in enumerate(references, 1):
            self.logger.info(f"Enriching reference {i}/{total}")
            enriched_ref = self.enrich_reference(ref)
            enriched.append(enriched_ref)

        return enriched
