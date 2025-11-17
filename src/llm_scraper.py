"""
LLM-Based Web Scraper Module
Uses Claude AI to intelligently extract structured data from web pages
Similar to Firecrawl but using Anthropic's Claude API
"""

import time
import logging
import requests
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
import os

# Try to import Anthropic
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic library not available. Install with: pip install anthropic")


class LLMScraper:
    """
    LLM-powered web scraper that uses Claude to extract structured data

    Features:
    - Converts HTML to clean markdown
    - Uses LLM to understand and extract data
    - Robust to HTML structure changes
    - No need for brittle CSS selectors
    - Handles complex, dynamic content
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        rate_limit: float = 1.0,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize LLM scraper

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Claude model to use
            rate_limit: Minimum seconds between requests
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.logger = logging.getLogger(__name__)
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_retries = max_retries
        self.last_request_time = 0
        self.model = model

        # Initialize API key
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic library required. Install with: pip install anthropic"
            )

        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment "
                "variable or pass api_key parameter"
            )

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)

        # Initialize user agent rotation
        self.ua = UserAgent()

        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            sleep_time = self.rate_limit - elapsed
            self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch web page content with retry logic

        Args:
            url: URL to fetch

        Returns:
            Page HTML content or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()

                # Rotate user agent
                self.session.headers['User-Agent'] = self.ua.random

                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                return response.text

            except Exception as e:
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed for {url}: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(
                        f"Failed to fetch {url} after {self.max_retries} attempts"
                    )
                    return None

    def html_to_markdown(self, html: str, base_url: str = "") -> str:
        """
        Convert HTML to clean markdown text

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            Markdown formatted text
        """
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "iframe"]):
            script.decompose()

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
            comment.extract()

        # Get text content
        text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        text = '\n'.join(lines)

        # Extract links if needed
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            link_text = a.get_text(strip=True)
            if href and link_text:
                absolute_url = urljoin(base_url, href)
                links.append(f"[{link_text}]({absolute_url})")

        # Add links section if any found
        if links:
            text += "\n\n## Links Found:\n" + "\n".join(links)

        return text

    def extract_with_llm(
        self,
        content: str,
        extraction_schema: Dict[str, Any],
        additional_context: str = ""
    ) -> Dict[str, Any]:
        """
        Use Claude to extract structured data from content

        Args:
            content: Text content to extract from
            extraction_schema: Schema describing what to extract
            additional_context: Additional context for the LLM

        Returns:
            Extracted structured data
        """
        # Build extraction prompt
        schema_description = self._build_schema_description(extraction_schema)

        prompt = f"""You are a data extraction expert. Extract structured information from the following content according to the schema below.

EXTRACTION SCHEMA:
{schema_description}

{additional_context}

CONTENT TO EXTRACT FROM:
{content[:15000]}  # Limit content size

Please extract the requested information and return it as a valid JSON object matching the schema. If a field is not found, use null. Be precise and only extract information that is explicitly present in the content.

Return ONLY the JSON object, no additional text."""

        try:
            self._rate_limit()

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to parse JSON
            # Look for JSON in code blocks or raw text
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object in response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = response_text

            extracted_data = json.loads(json_str)

            return extracted_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from LLM response: {e}")
            self.logger.debug(f"Response was: {response_text}")
            return {}
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {e}")
            return {}

    def _build_schema_description(self, schema: Dict[str, Any]) -> str:
        """
        Build human-readable schema description for LLM

        Args:
            schema: Dictionary describing the schema

        Returns:
            Formatted schema description
        """
        lines = []
        for field, config in schema.items():
            if isinstance(config, dict):
                field_type = config.get('type', 'string')
                description = config.get('description', '')
                required = config.get('required', False)

                req_text = " (REQUIRED)" if required else " (optional)"
                lines.append(f"- {field} ({field_type}){req_text}: {description}")
            else:
                # Simple schema: field: description
                lines.append(f"- {field}: {config}")

        return "\n".join(lines)

    def scrape_page(
        self,
        url: str,
        extraction_schema: Dict[str, Any],
        additional_context: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape a single page and extract structured data

        Args:
            url: URL to scrape
            extraction_schema: Schema for data extraction
            additional_context: Additional context for extraction

        Returns:
            Extracted data dictionary or None
        """
        self.logger.info(f"Scraping {url}")

        # Fetch page
        html = self.fetch_page(url)
        if not html:
            return None

        # Convert to markdown
        markdown = self.html_to_markdown(html, base_url=url)

        # Extract with LLM
        extracted = self.extract_with_llm(markdown, extraction_schema, additional_context)

        # Add metadata
        extracted['_metadata'] = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'model': self.model
        }

        return extracted

    def scrape_multiple_pages(
        self,
        urls: List[str],
        extraction_schema: Dict[str, Any],
        additional_context: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple pages

        Args:
            urls: List of URLs to scrape
            extraction_schema: Schema for data extraction
            additional_context: Additional context for extraction

        Returns:
            List of extracted data dictionaries
        """
        results = []

        for url in urls:
            try:
                data = self.scrape_page(url, extraction_schema, additional_context)
                if data:
                    results.append(data)
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                continue

        return results

    def scrape_to_dataframe(
        self,
        urls: List[str],
        extraction_schema: Dict[str, Any],
        additional_context: str = ""
    ) -> pd.DataFrame:
        """
        Scrape multiple pages and return as DataFrame

        Args:
            urls: List of URLs to scrape
            extraction_schema: Schema for data extraction
            additional_context: Additional context for extraction

        Returns:
            DataFrame with scraped data
        """
        results = self.scrape_multiple_pages(urls, extraction_schema, additional_context)

        if results:
            df = pd.DataFrame(results)
            self.logger.info(f"Created DataFrame with {len(df)} records")
            return df
        else:
            self.logger.warning("No data scraped")
            return pd.DataFrame()

    def search_and_extract(
        self,
        search_url: str,
        search_params: Dict[str, str],
        result_extraction_schema: Dict[str, Any],
        max_results: int = 100,
        pagination_strategy: str = "auto"
    ) -> List[Dict[str, Any]]:
        """
        Search a website and extract results

        Args:
            search_url: Base search URL
            search_params: Search parameters
            result_extraction_schema: Schema for extracting search results
            max_results: Maximum results to extract
            pagination_strategy: How to handle pagination ("auto", "none")

        Returns:
            List of extracted results
        """
        self.logger.info(f"Searching {search_url} with params: {search_params}")

        results = []
        page = 1

        while len(results) < max_results:
            # Build search URL
            params = search_params.copy()
            if pagination_strategy == "auto":
                params['page'] = page

            # Fetch search results page
            html = self.fetch_page(search_url)
            if not html:
                break

            # Convert to markdown
            markdown = self.html_to_markdown(html, base_url=search_url)

            # Extract results using LLM
            extraction_prompt = f"""Extract all search results as a JSON array.
Each result should match the schema. Return as: {{"results": [...array of results...]}}"""

            page_data = self.extract_with_llm(
                markdown,
                result_extraction_schema,
                extraction_prompt
            )

            page_results = page_data.get('results', [])
            if isinstance(page_results, dict):
                page_results = [page_results]

            if not page_results:
                # No more results
                break

            results.extend(page_results)

            if pagination_strategy == "none":
                break

            page += 1

        return results[:max_results]

    def extract_download_links(
        self,
        url: str,
        link_patterns: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Extract download links from a page

        Args:
            url: URL to scrape
            link_patterns: List of regex patterns to match (e.g., [r'\.csv$', r'\.zip$'])

        Returns:
            List of download link dictionaries
        """
        self.logger.info(f"Extracting download links from {url}")

        html = self.fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        links = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            link_text = a.get_text(strip=True)
            absolute_url = urljoin(url, href)

            # Check if matches patterns
            if link_patterns:
                matches = any(re.search(pattern, absolute_url, re.I) for pattern in link_patterns)
                if not matches:
                    continue

            links.append({
                'url': absolute_url,
                'text': link_text,
                'filename': Path(urlparse(absolute_url).path).name,
                'found_at': datetime.now().isoformat()
            })

        self.logger.info(f"Found {len(links)} download links")
        return links

    def download_file(self, url: str, output_path: Path) -> bool:
        """
        Download a file from URL

        Args:
            url: URL to download from
            output_path: Path to save file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Downloading {url}")

            response = self.session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            output_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                from tqdm import tqdm
                use_tqdm = True
            except ImportError:
                use_tqdm = False

            with open(output_path, 'wb') as f:
                if use_tqdm and total_size > 0:
                    with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            size = f.write(chunk)
                            pbar.update(size)
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            self.logger.info(f"Downloaded to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False

    def close(self):
        """Close the session and cleanup resources"""
        self.session.close()
        self.logger.info("LLM scraper session closed")


class BusinessLLMScraper:
    """
    High-level LLM scraper for business data extraction
    Specialized for extracting business entity information
    """

    # Default schema for business entity extraction
    BUSINESS_SCHEMA = {
        'entity_number': {
            'type': 'string',
            'description': 'Business entity number or ID',
            'required': False
        },
        'entity_name': {
            'type': 'string',
            'description': 'Official business name',
            'required': True
        },
        'entity_type': {
            'type': 'string',
            'description': 'Type of business entity (LLC, Corporation, etc.)',
            'required': False
        },
        'status': {
            'type': 'string',
            'description': 'Current status (Active, Suspended, Dissolved, etc.)',
            'required': False
        },
        'registration_date': {
            'type': 'string',
            'description': 'Date business was registered',
            'required': False
        },
        'jurisdiction': {
            'type': 'string',
            'description': 'Jurisdiction of registration',
            'required': False
        },
        'agent_name': {
            'type': 'string',
            'description': 'Registered agent name',
            'required': False
        },
        'principal_address': {
            'type': 'string',
            'description': 'Principal business address',
            'required': False
        },
        'mailing_address': {
            'type': 'string',
            'description': 'Mailing address',
            'required': False
        },
        'city': {
            'type': 'string',
            'description': 'City',
            'required': False
        },
        'state': {
            'type': 'string',
            'description': 'State',
            'required': False
        },
        'zip_code': {
            'type': 'string',
            'description': 'ZIP code',
            'required': False
        }
    }

    def __init__(self, api_key: Optional[str] = None, output_dir: str = "./scraped_data"):
        """
        Initialize business LLM scraper

        Args:
            api_key: Anthropic API key
            output_dir: Directory to save scraped data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.scraper = LLMScraper(api_key=api_key)

    def scrape_business(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape business information from a URL

        Args:
            url: URL of business page

        Returns:
            Business data dictionary
        """
        return self.scraper.scrape_page(
            url,
            self.BUSINESS_SCHEMA,
            additional_context="This is a business entity information page. Extract all available business details."
        )

    def scrape_businesses(self, urls: List[str]) -> pd.DataFrame:
        """
        Scrape multiple business pages

        Args:
            urls: List of business page URLs

        Returns:
            DataFrame with business data
        """
        return self.scraper.scrape_to_dataframe(
            urls,
            self.BUSINESS_SCHEMA,
            additional_context="Extract business entity information from these pages."
        )

    def search_businesses(
        self,
        search_url: str,
        business_name: Optional[str] = None,
        entity_number: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for businesses

        Args:
            search_url: Base search URL
            business_name: Business name to search for
            entity_number: Entity number to search for
            max_results: Maximum results to return

        Returns:
            List of business data dictionaries
        """
        search_params = {}
        if business_name:
            search_params['name'] = business_name
        if entity_number:
            search_params['number'] = entity_number

        return self.scraper.search_and_extract(
            search_url,
            search_params,
            self.BUSINESS_SCHEMA,
            max_results=max_results
        )

    def discover_bulk_downloads(
        self,
        url: str,
        download_patterns: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Discover bulk data download links

        Args:
            url: URL to search for downloads
            download_patterns: File patterns to look for

        Returns:
            List of download information
        """
        if download_patterns is None:
            download_patterns = [r'\.(zip|csv|txt|xlsx)$']

        return self.scraper.extract_download_links(url, download_patterns)

    def scrape_and_save(
        self,
        urls: List[str],
        output_filename: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Path]:
        """
        Scrape businesses and save to file

        Args:
            urls: List of business page URLs
            output_filename: Optional output filename

        Returns:
            Tuple of (DataFrame, output_path)
        """
        self.logger.info(f"Scraping {len(urls)} business pages...")

        df = self.scrape_businesses(urls)

        if df.empty:
            self.logger.warning("No data scraped")
            return df, None

        # Save to file
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"llm_scraped_businesses_{timestamp}.csv"

        output_path = self.output_dir / output_filename
        df.to_csv(output_path, index=False)

        self.logger.info(f"Saved {len(df)} records to {output_path}")

        return df, output_path

    def close(self):
        """Cleanup resources"""
        self.scraper.close()
