"""Content extraction engine using LLM providers."""

from typing import Any, Optional

from ..llm import get_provider, LLMProvider
from .web_scraper import WebScraper, ScrapedContent


class ContentExtractor:
    """Main extraction engine that combines scraping and LLM extraction."""

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **provider_kwargs
    ):
        """
        Initialize the content extractor.

        Args:
            provider: LLM provider name (openai, anthropic, google, ollama)
            api_key: API key for the provider
            model: Model name to use
            **provider_kwargs: Additional provider-specific arguments
        """
        self.llm = get_provider(provider, api_key, model, **provider_kwargs)
        self.scraper = WebScraper()

    def set_provider(
        self,
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """Switch to a different LLM provider."""
        self.llm = get_provider(provider, api_key, model, **kwargs)

    async def extract_from_url(
        self,
        url: str,
        schema: dict[str, Any],
        instructions: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Extract structured data from a URL.

        Args:
            url: URL to scrape and extract from
            schema: Schema defining what to extract
            instructions: Optional extraction instructions

        Returns:
            Extracted data as a dictionary
        """
        # Scrape the content
        scraped = await self.scraper.scrape(url)

        # Extract using LLM
        result = await self.llm.extract_structured(
            content=scraped.text,
            schema=schema,
            instructions=instructions
        )

        # Add metadata
        result["_source"] = {
            "url": url,
            "title": scraped.title,
            "provider": self.llm.name,
            "model": self.llm.model
        }

        return result

    async def extract_from_text(
        self,
        text: str,
        schema: dict[str, Any],
        instructions: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Extract structured data from raw text.

        Args:
            text: Text content to extract from
            schema: Schema defining what to extract
            instructions: Optional extraction instructions

        Returns:
            Extracted data as a dictionary
        """
        result = await self.llm.extract_structured(
            content=text,
            schema=schema,
            instructions=instructions
        )

        result["_source"] = {
            "provider": self.llm.name,
            "model": self.llm.model
        }

        return result

    async def extract_from_html(
        self,
        html: str,
        schema: dict[str, Any],
        instructions: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Extract structured data from HTML content.

        Args:
            html: HTML content to parse and extract from
            schema: Schema defining what to extract
            instructions: Optional extraction instructions

        Returns:
            Extracted data as a dictionary
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")

        # Remove scripts and styles
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        text = soup.get_text(separator="\n", strip=True)

        return await self.extract_from_text(text, schema, instructions)

    async def batch_extract(
        self,
        urls: list[str],
        schema: dict[str, Any],
        instructions: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Extract data from multiple URLs.

        Args:
            urls: List of URLs to process
            schema: Schema defining what to extract
            instructions: Optional extraction instructions

        Returns:
            List of extracted data dictionaries
        """
        import asyncio

        tasks = [
            self.extract_from_url(url, schema, instructions)
            for url in urls
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append({
                    "error": str(result),
                    "_source": {"url": urls[i]}
                })
            else:
                processed.append(result)

        return processed
