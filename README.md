# Firecrawl LLM Extraction

A Firecrawl-style LLM data extraction tool that allows you to extract structured data from web pages using AI. Features provider switching from both CLI and Web UI.

## Features

- **Multiple LLM Providers**: OpenAI, Anthropic Claude, Google Gemini, Ollama (local)
- **Provider Switching**: Switch between providers via CLI flags or Web UI
- **Schema-based Extraction**: Define what data to extract using JSON schemas
- **Batch Processing**: Process multiple URLs at once
- **Web UI**: User-friendly interface for extraction tasks
- **CLI Tool**: Command-line interface for automation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Business-Data-Extraction-workflow.git
cd Business-Data-Extraction-workflow
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Set your API keys in the `.env` file:

```env
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
DEFAULT_LLM_PROVIDER=openai
```

## CLI Usage

### Extract from URL

```bash
# Basic extraction with default provider
python -m src.cli.main extract "https://example.com"

# Specify provider
python -m src.cli.main extract "https://example.com" --provider anthropic

# Use custom schema
python -m src.cli.main extract "https://example.com" --schema schema.json

# With inline schema
python -m src.cli.main extract "https://example.com" \
    --schema '{"title": "string", "summary": "string"}'
```

### Switch Providers

```bash
# Use OpenAI
python -m src.cli.main extract "https://example.com" --provider openai --model gpt-4-turbo

# Use Anthropic Claude
python -m src.cli.main extract "https://example.com" --provider anthropic --model claude-3-opus-20240229

# Use Google Gemini
python -m src.cli.main extract "https://example.com" --provider google

# Use local Ollama
python -m src.cli.main extract "https://example.com" --provider ollama --model llama2
```

### List Providers

```bash
python -m src.cli.main providers
```

### Test Provider

```bash
python -m src.cli.main test-provider openai
python -m src.cli.main test-provider anthropic
```

### Batch Processing

```bash
# Create a file with URLs (one per line)
echo "https://example1.com" > urls.txt
echo "https://example2.com" >> urls.txt

# Process batch
python -m src.cli.main batch urls.txt --schema schema.json --output results.json
```

### Start Web Server

```bash
python -m src.cli.main serve
# Or with custom host/port
python -m src.cli.main serve --host 0.0.0.0 --port 8080
```

## Web UI

Start the web server and open http://localhost:8000 in your browser.

### Features:
- **Provider Selection**: Switch between providers using the dropdown
- **Model Configuration**: Specify custom models
- **Multiple Input Types**: URL, raw text, or HTML
- **Schema Editor**: Define extraction schemas with JSON
- **Example Templates**: Pre-built schemas for common use cases

## API Endpoints

### Extract Data
```bash
POST /api/extract
{
    "url": "https://example.com",
    "schema_def": {
        "title": {"type": "string", "description": "Page title"},
        "summary": {"type": "string", "description": "Content summary"}
    },
    "provider": "openai",
    "instructions": "Focus on technical details"
}
```

### Switch Provider
```bash
POST /api/config
{
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229"
}
```

### List Providers
```bash
GET /api/providers
```

### Test Provider
```bash
POST /api/test-provider?provider=openai
```

## Schema Format

Define extraction schemas as JSON objects:

```json
{
    "field_name": {
        "type": "string|number|array|object",
        "description": "Description of what to extract"
    }
}
```

### Example Schemas

**Business Information:**
```json
{
    "company_name": {"type": "string", "description": "Company name"},
    "industry": {"type": "string", "description": "Industry sector"},
    "employees": {"type": "string", "description": "Number of employees"},
    "headquarters": {"type": "string", "description": "HQ location"}
}
```

**Article:**
```json
{
    "title": {"type": "string", "description": "Article title"},
    "author": {"type": "string", "description": "Author name"},
    "summary": {"type": "string", "description": "Article summary"},
    "main_points": {"type": "array", "description": "Key points"}
}
```

## Project Structure

```
Business-Data-Extraction-workflow/
├── src/
│   ├── llm/                 # LLM provider implementations
│   │   ├── base.py          # Abstract base class
│   │   ├── factory.py       # Provider factory
│   │   ├── openai_provider.py
│   │   ├── anthropic_provider.py
│   │   ├── google_provider.py
│   │   └── ollama_provider.py
│   ├── extractors/          # Extraction modules
│   │   ├── web_scraper.py   # Web scraping
│   │   └── content_extractor.py
│   ├── api/                 # FastAPI backend
│   │   └── main.py
│   ├── cli/                 # CLI implementation
│   │   └── main.py
│   └── ui/                  # Web UI
│       ├── templates/
│       └── static/
├── config/
│   └── settings.py
├── requirements.txt
├── .env.example
└── README.md
```

## Development

### Run Tests
```bash
pytest tests/
```

### Development Server
```bash
python -m src.cli.main serve --reload
```

## License

MIT License
