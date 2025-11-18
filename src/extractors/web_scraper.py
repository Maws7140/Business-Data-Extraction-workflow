"""Web scraping utilities for fetching content."""

import os
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel


class ScrapedContent(BaseModel):
    """Container for scraped web content."""

    url: str
    title: str
    text: str
    html: str
    links: list[str] = []
    metadata: dict = {}


class WebScraper:
    """Web scraper for fetching and parsing web pages."""

    def __init__(
        self,
        timeout: int = 30,
        max_content_length: int = 100000,
        user_agent: Optional[str] = None
    ):
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.user_agent = user_agent or "FirecrawlLLM/1.0 (Business Data Extraction)"

    async def scrape(self, url: str) -> ScrapedContent:
        """
        Scrape content from a URL.

        Args:
            url: The URL to scrape

        Returns:
            ScrapedContent with extracted text and metadata
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        html = response.text
        if len(html) > self.max_content_length:
            html = html[:self.max_content_length]

        soup = BeautifulSoup(html, "lxml")

        # Remove script and style elements
        for element in soup(["script", "style", "noscript", "iframe"]):
            element.decompose()

        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string or ""

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

        # Clean up text - remove excessive newlines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

        # Extract links
        links = []
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.startswith("/"):
                href = urljoin(base_url, href)
            if href.startswith("http"):
                links.append(href)

        # Extract metadata
        metadata = self._extract_metadata(soup)

        return ScrapedContent(
            url=url,
            title=title,
            text=text,
            html=html,
            links=links[:100],  # Limit links
            metadata=metadata
        )

    def _extract_metadata(self, soup: BeautifulSoup) -> dict:
        """Extract metadata from HTML."""
        metadata = {}

        # Meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property", "")
            content = meta.get("content", "")
            if name and content:
                metadata[name] = content

        # OpenGraph tags
        for og in soup.find_all("meta", property=lambda x: x and x.startswith("og:")):
            prop = og.get("property", "").replace("og:", "")
            content = og.get("content", "")
            if prop and content:
                metadata[f"og_{prop}"] = content

        return metadata

    async def scrape_multiple(self, urls: list[str]) -> list[ScrapedContent]:
        """Scrape multiple URLs concurrently."""
        import asyncio

        tasks = [self.scrape(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = []
        for result in results:
            if isinstance(result, ScrapedContent):
                successful.append(result)

        return successful
