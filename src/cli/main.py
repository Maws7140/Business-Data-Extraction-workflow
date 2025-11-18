"""Main CLI application for Firecrawl-style LLM extraction."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.extractors import ContentExtractor
from src.llm import list_providers
from config.settings import settings

app = typer.Typer(
    name="firecrawl-llm",
    help="Firecrawl-style LLM data extraction tool with provider switching",
    add_completion=False
)
console = Console()


@app.command()
def extract(
    url: str = typer.Argument(..., help="URL to extract data from"),
    schema: str = typer.Option(
        None,
        "--schema", "-s",
        help="JSON schema file or inline JSON defining what to extract"
    ),
    provider: str = typer.Option(
        None,
        "--provider", "-p",
        help=f"LLM provider to use ({', '.join(list_providers())})"
    ),
    model: str = typer.Option(
        None,
        "--model", "-m",
        help="Model name to use (provider-specific)"
    ),
    instructions: str = typer.Option(
        None,
        "--instructions", "-i",
        help="Additional extraction instructions"
    ),
    output: str = typer.Option(
        None,
        "--output", "-o",
        help="Output file path (default: stdout)"
    ),
    pretty: bool = typer.Option(
        True,
        "--pretty/--compact",
        help="Pretty print JSON output"
    )
):
    """Extract structured data from a URL using LLM."""

    # Parse schema
    if schema:
        if os.path.isfile(schema):
            with open(schema) as f:
                schema_dict = json.load(f)
        else:
            try:
                schema_dict = json.loads(schema)
            except json.JSONDecodeError:
                console.print("[red]Error: Invalid JSON schema[/red]")
                raise typer.Exit(1)
    else:
        # Default schema for general extraction
        schema_dict = {
            "title": {"type": "string", "description": "Page title"},
            "summary": {"type": "string", "description": "Brief summary of the content"},
            "main_topics": {"type": "array", "description": "Main topics discussed"},
            "key_information": {"type": "object", "description": "Key facts and data points"}
        }

    # Get provider
    provider_name = provider or settings.default_llm_provider

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task(f"Extracting from {url} using {provider_name}...", total=None)

        try:
            extractor = ContentExtractor(
                provider=provider_name,
                model=model,
                api_key=settings.get_api_key(provider_name)
            )

            result = asyncio.run(
                extractor.extract_from_url(url, schema_dict, instructions)
            )
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    # Output result
    json_output = json.dumps(result, indent=2 if pretty else None, ensure_ascii=False)

    if output:
        with open(output, "w") as f:
            f.write(json_output)
        console.print(f"[green]Output saved to {output}[/green]")
    else:
        syntax = Syntax(json_output, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Extraction Result", border_style="green"))


@app.command()
def batch(
    urls_file: str = typer.Argument(..., help="File containing URLs (one per line)"),
    schema: str = typer.Option(..., "--schema", "-s", help="JSON schema file"),
    provider: str = typer.Option(None, "--provider", "-p", help="LLM provider to use"),
    model: str = typer.Option(None, "--model", "-m", help="Model name to use"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Extract data from multiple URLs in batch."""

    # Read URLs
    with open(urls_file) as f:
        urls = [line.strip() for line in f if line.strip()]

    # Load schema
    with open(schema) as f:
        schema_dict = json.load(f)

    provider_name = provider or settings.default_llm_provider

    console.print(f"Processing {len(urls)} URLs with {provider_name}...")

    try:
        extractor = ContentExtractor(
            provider=provider_name,
            model=model,
            api_key=settings.get_api_key(provider_name)
        )

        results = asyncio.run(extractor.batch_extract(urls, schema_dict))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Output
    json_output = json.dumps(results, indent=2, ensure_ascii=False)

    if output:
        with open(output, "w") as f:
            f.write(json_output)
        console.print(f"[green]Results saved to {output}[/green]")
    else:
        console.print(json_output)


@app.command()
def providers():
    """List available LLM providers and their status."""

    table = Table(title="Available LLM Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Default Model", style="magenta")
    table.add_column("API Key Set", style="green")
    table.add_column("Default", style="yellow")

    provider_list = list_providers()

    for provider in provider_list:
        model = settings.get_model(provider)
        api_key = settings.get_api_key(provider)
        has_key = "Yes" if api_key or provider == "ollama" else "No"
        is_default = "**" if provider == settings.default_llm_provider else ""

        table.add_row(provider, model, has_key, is_default)

    console.print(table)
    console.print(f"\nDefault provider: [cyan]{settings.default_llm_provider}[/cyan]")
    console.print("Set DEFAULT_LLM_PROVIDER environment variable to change default")


@app.command()
def config():
    """Show current configuration."""

    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Default Provider", settings.default_llm_provider)
    table.add_row("Server Host", settings.host)
    table.add_row("Server Port", str(settings.port))
    table.add_row("Debug Mode", str(settings.debug))
    table.add_row("Max Content Length", str(settings.max_content_length))
    table.add_row("Request Timeout", f"{settings.request_timeout}s")

    console.print(table)


@app.command()
def serve(
    host: str = typer.Option(None, "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(None, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload")
):
    """Start the web UI server."""
    import uvicorn

    host = host or settings.host
    port = port or settings.port

    console.print(f"Starting server at http://{host}:{port}")
    console.print("Press CTRL+C to stop")

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload
    )


@app.command()
def test_provider(
    provider: str = typer.Argument(..., help="Provider to test"),
    model: str = typer.Option(None, "--model", "-m", help="Model to test")
):
    """Test a provider connection."""

    console.print(f"Testing {provider}...")

    try:
        extractor = ContentExtractor(
            provider=provider,
            model=model,
            api_key=settings.get_api_key(provider)
        )

        # Simple test
        result = asyncio.run(
            extractor.extract_from_text(
                "The capital of France is Paris. It has a population of 2.1 million.",
                schema={
                    "capital": "string",
                    "country": "string",
                    "population": "string"
                }
            )
        )

        console.print(f"[green]Success![/green] Provider {provider} is working.")
        console.print(f"Result: {json.dumps(result, indent=2)}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
