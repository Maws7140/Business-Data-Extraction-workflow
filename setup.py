"""Setup file for the package."""

from setuptools import setup, find_packages

setup(
    name="firecrawl-llm-extraction",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "openai>=1.3.0",
        "anthropic>=0.7.0",
        "google-generativeai>=0.3.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "httpx>=0.25.0",
        "lxml>=4.9.0",
        "typer[all]>=0.9.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "jinja2>=3.1.2",
        "aiofiles>=23.2.0",
    ],
    entry_points={
        "console_scripts": [
            "firecrawl-llm=src.cli.main:main",
        ],
    },
    python_requires=">=3.10",
    author="Your Name",
    description="Firecrawl-style LLM data extraction with provider switching",
)
