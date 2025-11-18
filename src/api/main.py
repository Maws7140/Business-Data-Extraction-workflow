"""FastAPI application for the web UI and API."""

import json
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.extractors import ContentExtractor
from src.llm import list_providers
from config.settings import settings

app = FastAPI(
    title="Firecrawl LLM Extraction",
    description="Firecrawl-style LLM data extraction with provider switching",
    version="0.1.0"
)

# Mount static files
static_path = Path(__file__).parent.parent / "ui" / "static"
templates_path = Path(__file__).parent.parent / "ui" / "templates"

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

templates = Jinja2Templates(directory=str(templates_path))


# Request/Response models
class ExtractionRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None
    schema_def: dict[str, Any]
    instructions: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class ExtractionResponse(BaseModel):
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class ProviderInfo(BaseModel):
    name: str
    default_model: str
    has_api_key: bool
    is_default: bool


class ConfigUpdate(BaseModel):
    provider: str
    model: Optional[str] = None


# In-memory session config (in production, use a proper session store)
session_config = {
    "provider": settings.default_llm_provider,
    "model": None
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main UI page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "providers": list_providers(),
            "current_provider": session_config["provider"],
            "current_model": session_config["model"]
        }
    )


@app.get("/api/providers")
async def get_providers() -> list[ProviderInfo]:
    """Get list of available providers."""
    providers = []
    for name in list_providers():
        providers.append(ProviderInfo(
            name=name,
            default_model=settings.get_model(name),
            has_api_key=bool(settings.get_api_key(name)) or name == "ollama",
            is_default=name == session_config["provider"]
        ))
    return providers


@app.get("/api/config")
async def get_config():
    """Get current session configuration."""
    return {
        "provider": session_config["provider"],
        "model": session_config["model"] or settings.get_model(session_config["provider"]),
        "available_providers": list_providers()
    }


@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    """Update session configuration (switch provider)."""
    if config.provider not in list_providers():
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider: {config.provider}"
        )

    session_config["provider"] = config.provider
    session_config["model"] = config.model

    return {
        "success": True,
        "provider": session_config["provider"],
        "model": session_config["model"] or settings.get_model(config.provider)
    }


@app.post("/api/extract", response_model=ExtractionResponse)
async def extract(request: ExtractionRequest):
    """Extract structured data from content."""

    # Determine provider
    provider = request.provider or session_config["provider"]
    model = request.model or session_config["model"]

    try:
        extractor = ContentExtractor(
            provider=provider,
            model=model,
            api_key=settings.get_api_key(provider)
        )

        # Extract based on input type
        if request.url:
            result = await extractor.extract_from_url(
                request.url,
                request.schema_def,
                request.instructions
            )
        elif request.html:
            result = await extractor.extract_from_html(
                request.html,
                request.schema_def,
                request.instructions
            )
        elif request.text:
            result = await extractor.extract_from_text(
                request.text,
                request.schema_def,
                request.instructions
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide url, text, or html"
            )

        return ExtractionResponse(success=True, data=result)

    except Exception as e:
        return ExtractionResponse(success=False, error=str(e))


@app.post("/api/test-provider")
async def test_provider(provider: str, model: Optional[str] = None):
    """Test a provider connection."""
    try:
        extractor = ContentExtractor(
            provider=provider,
            model=model,
            api_key=settings.get_api_key(provider)
        )

        result = await extractor.extract_from_text(
            "Test: Paris is the capital of France.",
            schema={"capital": "string", "country": "string"}
        )

        return {"success": True, "result": result}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
