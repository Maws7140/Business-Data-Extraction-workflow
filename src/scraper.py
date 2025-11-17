"""
Web Scraper Module for California Secretary of State Business Data
Handles scraping of business entity data from CA SOS website
"""

import time
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import json

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import pandas as pd


class CAScraper:
    """
    Web scraper for California Secretary of State business data

    Supports:
    - Scraping individual business records from search
    - Finding bulk data download links
    - Extracting business entity information
    """

    # California SOS URLs
    BASE_URL = "https://bizfileonline.sos.ca.gov"
    SEARCH_URL = "https://bizfileonline.sos.ca.gov/search/business"

    def __init__(self, headless: bool = True, rate_limit: float = 1.0,
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialize the CA SOS scraper

        Args:
            headless: Run browser in headless mode
            rate_limit: Minimum seconds between requests (rate limiting)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.logger = logging.getLogger(__name__)
        self.headless = headless
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_retries = max_retries
        self.last_request_time = 0

        # Initialize user agent rotation
        self.ua = UserAgent()

        # Session for regular requests
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

    def _get_selenium_driver(self) -> webdriver.Chrome:
        """
        Initialize and return Selenium WebDriver

        Returns:
            Configured Chrome WebDriver instance
        """
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'user-agent={self.ua.random}')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def fetch_page(self, url: str, use_selenium: bool = False) -> Optional[str]:
        """
        Fetch web page content with retry logic

        Args:
            url: URL to fetch
            use_selenium: Whether to use Selenium instead of requests

        Returns:
            Page HTML content or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()

                if use_selenium:
                    driver = self._get_selenium_driver()
                    try:
                        driver.get(url)
                        time.sleep(2)  # Wait for page load
                        html = driver.page_source
                        return html
                    finally:
                        driver.quit()
                else:
                    # Rotate user agent
                    self.session.headers['User-Agent'] = self.ua.random
                    response = self.session.get(url, timeout=self.timeout)
                    response.raise_for_status()
                    return response.text

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None

    def search_business(self, business_name: str = None, entity_number: str = None,
                       max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search for businesses on CA SOS website

        Args:
            business_name: Business name to search for
            entity_number: Entity number to search for
            max_results: Maximum number of results to return

        Returns:
            List of business entity dictionaries
        """
        self.logger.info(f"Searching CA SOS for businesses...")

        results = []

        # Note: This is a simplified implementation
        # The actual CA SOS website may require form submissions, JavaScript, etc.
        # This provides the framework for scraping

        if entity_number:
            # Search by entity number
            result = self._scrape_business_detail(entity_number)
            if result:
                results.append(result)
        elif business_name:
            # Search by business name
            results = self._scrape_business_search(business_name, max_results)

        self.logger.info(f"Found {len(results)} business records")
        return results

    def _scrape_business_search(self, business_name: str,
                               max_results: int) -> List[Dict[str, Any]]:
        """
        Scrape business search results

        Args:
            business_name: Business name to search
            max_results: Maximum results to retrieve

        Returns:
            List of business entity dictionaries
        """
        results = []

        try:
            # This is a template - actual implementation depends on CA SOS website structure
            driver = self._get_selenium_driver()

            try:
                driver.get(self.SEARCH_URL)

                # Wait for search form
                wait = WebDriverWait(driver, 10)

                # Find and fill search input
                # Note: Selectors may need to be updated based on actual website
                try:
                    search_input = wait.until(
                        EC.presence_of_element_located((By.ID, "SearchCriteria"))
                    )
                    search_input.clear()
                    search_input.send_keys(business_name)

                    # Submit search
                    search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    search_button.click()

                    # Wait for results
                    time.sleep(3)

                    # Parse results
                    soup = BeautifulSoup(driver.page_source, 'lxml')

                    # Extract business records from results table
                    # This is a template - selectors need to match actual website
                    result_rows = soup.select('table.search-results tr')

                    for row in result_rows[:max_results]:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            business_data = {
                                'entity_number': cells[0].get_text(strip=True),
                                'entity_name': cells[1].get_text(strip=True),
                                'entity_type': cells[2].get_text(strip=True),
                                'status': cells[3].get_text(strip=True) if len(cells) > 3 else None,
                                'scraped_at': datetime.now().isoformat()
                            }
                            results.append(business_data)

                except (TimeoutException, NoSuchElementException) as e:
                    self.logger.warning(f"Could not find search elements: {e}")

            finally:
                driver.quit()

        except Exception as e:
            self.logger.error(f"Error scraping business search: {e}")

        return results

    def _scrape_business_detail(self, entity_number: str) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed business information for a specific entity

        Args:
            entity_number: CA entity number

        Returns:
            Business entity dictionary or None
        """
        try:
            detail_url = f"{self.BASE_URL}/search/business/{entity_number}"
            html = self.fetch_page(detail_url, use_selenium=True)

            if not html:
                return None

            soup = BeautifulSoup(html, 'lxml')

            # Extract business details
            # Template - selectors need to match actual website structure
            business_data = {
                'entity_number': entity_number,
                'entity_name': self._extract_text(soup, 'span.entity-name'),
                'entity_type': self._extract_text(soup, 'span.entity-type'),
                'status': self._extract_text(soup, 'span.status'),
                'registration_date': self._extract_text(soup, 'span.registration-date'),
                'jurisdiction': self._extract_text(soup, 'span.jurisdiction'),
                'agent_name': self._extract_text(soup, 'span.agent-name'),
                'principal_address': self._extract_text(soup, 'div.principal-address'),
                'mailing_address': self._extract_text(soup, 'div.mailing-address'),
                'scraped_at': datetime.now().isoformat()
            }

            return business_data

        except Exception as e:
            self.logger.error(f"Error scraping business detail for {entity_number}: {e}")
            return None

    def _extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """
        Extract text from HTML element using CSS selector

        Args:
            soup: BeautifulSoup object
            selector: CSS selector

        Returns:
            Extracted text or None
        """
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None

    def scrape_bulk_data_links(self) -> List[Dict[str, str]]:
        """
        Scrape available bulk data download links from CA SOS

        Returns:
            List of dictionaries with download information
        """
        self.logger.info("Scraping bulk data download links...")

        bulk_data_url = "https://www.sos.ca.gov/business-programs/business-entities/download-data"

        downloads = []

        try:
            html = self.fetch_page(bulk_data_url)

            if html:
                soup = BeautifulSoup(html, 'lxml')

                # Find download links (adjust selectors based on actual page)
                links = soup.find_all('a', href=re.compile(r'\.(zip|csv|txt)$', re.I))

                for link in links:
                    href = link.get('href')
                    if href:
                        download_info = {
                            'url': urljoin(bulk_data_url, href),
                            'title': link.get_text(strip=True),
                            'filename': Path(urlparse(href).path).name,
                            'found_at': datetime.now().isoformat()
                        }
                        downloads.append(download_info)
                        self.logger.info(f"Found download: {download_info['title']}")

        except Exception as e:
            self.logger.error(f"Error scraping bulk data links: {e}")

        return downloads

    def scrape_to_dataframe(self, business_names: List[str] = None,
                           entity_numbers: List[str] = None,
                           max_per_search: int = 100) -> pd.DataFrame:
        """
        Scrape multiple businesses and return as DataFrame

        Args:
            business_names: List of business names to search
            entity_numbers: List of entity numbers to search
            max_per_search: Maximum results per search query

        Returns:
            DataFrame with scraped business data
        """
        all_results = []

        if business_names:
            for name in business_names:
                self.logger.info(f"Scraping businesses matching: {name}")
                results = self.search_business(business_name=name, max_results=max_per_search)
                all_results.extend(results)
                time.sleep(self.rate_limit)

        if entity_numbers:
            for number in entity_numbers:
                self.logger.info(f"Scraping entity: {number}")
                result = self.search_business(entity_number=number)
                all_results.extend(result)
                time.sleep(self.rate_limit)

        if all_results:
            df = pd.DataFrame(all_results)
            self.logger.info(f"Created DataFrame with {len(df)} records")
            return df
        else:
            self.logger.warning("No results scraped")
            return pd.DataFrame()

    def download_file(self, url: str, output_path: Path) -> bool:
        """
        Download a file from URL with progress bar

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

            from tqdm import tqdm

            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        size = f.write(chunk)
                        pbar.update(size)

            self.logger.info(f"Downloaded to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False

    def close(self):
        """Close the session and cleanup resources"""
        self.session.close()
        self.logger.info("Scraper session closed")


class BusinessDataScraper:
    """
    High-level scraper for business data extraction workflows
    Combines scraping with data processing
    """

    def __init__(self, output_dir: str = "./scraped_data"):
        """
        Initialize business data scraper

        Args:
            output_dir: Directory to save scraped data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.scraper = CAScraper()

    def scrape_and_save(self, search_config: Dict[str, Any],
                       output_filename: str = None) -> Tuple[pd.DataFrame, Path]:
        """
        Scrape data based on configuration and save to file

        Args:
            search_config: Dictionary with search parameters
                {
                    'business_names': ['Name1', 'Name2'],
                    'entity_numbers': ['123456', '789012'],
                    'max_results': 100
                }
            output_filename: Optional output filename

        Returns:
            Tuple of (DataFrame, output_path)
        """
        self.logger.info("Starting scraping workflow...")

        # Scrape data
        df = self.scraper.scrape_to_dataframe(
            business_names=search_config.get('business_names'),
            entity_numbers=search_config.get('entity_numbers'),
            max_per_search=search_config.get('max_results', 100)
        )

        if df.empty:
            self.logger.warning("No data scraped")
            return df, None

        # Save to file
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"scraped_businesses_{timestamp}.csv"

        output_path = self.output_dir / output_filename
        df.to_csv(output_path, index=False)

        self.logger.info(f"Saved {len(df)} records to {output_path}")

        return df, output_path

    def discover_bulk_downloads(self, download_all: bool = False,
                               output_dir: Optional[Path] = None) -> List[Dict[str, str]]:
        """
        Discover and optionally download bulk data files

        Args:
            download_all: Whether to download all discovered files
            output_dir: Directory to save downloads

        Returns:
            List of download information dictionaries
        """
        downloads = self.scraper.scrape_bulk_data_links()

        if download_all and downloads:
            if output_dir is None:
                output_dir = self.output_dir / "bulk_downloads"
            output_dir.mkdir(parents=True, exist_ok=True)

            for download in downloads:
                output_path = output_dir / download['filename']
                success = self.scraper.download_file(download['url'], output_path)
                download['downloaded'] = success
                download['local_path'] = str(output_path) if success else None

        return downloads

    def close(self):
        """Cleanup resources"""
        self.scraper.close()
