# Web UI User Guide

## Quick Start

### Linux/Mac
```bash
./start-ui.sh
```

### Windows
```bash
start-ui.bat
```

### Manual Start
```bash
python -m src.cli.main serve
```

Then open your browser to **http://localhost:8000**

---

## Web UI Features

### 1. Provider Configuration Section

**Switch between AI providers:**
- **OpenAI** - GPT-4 Turbo and other OpenAI models
- **Anthropic** - Claude 3 models (Opus, Sonnet, Haiku)
- **Google** - Gemini Pro
- **Ollama** - Local models (requires Ollama installed)

**How to use:**
1. Select provider from dropdown
2. (Optional) Enter custom model name
3. Click "Save Config" to apply
4. Click "Test Provider" to verify connection

---

### 2. Data Extraction Section

**Three input modes:**

#### URL Mode (Default)
- Enter any website URL
- System will scrape and extract data automatically
- Example: `https://example.com/about`

#### Text Mode
- Paste raw text content
- Useful for documents, articles, or copied content
- No web scraping needed

#### HTML Mode
- Paste HTML source code
- System extracts text and applies schema
- Good for local HTML files

---

### 3. Schema Definition

Define what data to extract using JSON format:

**Basic Schema:**
```json
{
  "field_name": {
    "type": "string",
    "description": "What to extract"
  }
}
```

**Type Options:**
- `string` - Text data
- `number` - Numeric values
- `array` - Lists of items
- `object` - Nested structures

**Example Schemas Available:**
Click the preset buttons to load common schemas:
- **Business Info** - Company details, industry, location
- **Article** - Title, author, summary, key points
- **Product** - Name, price, features, specifications
- **Contact Info** - Name, email, phone, address

---

### 4. Extraction Instructions (Optional)

Add custom instructions to guide the AI:
- "Focus on technical specifications"
- "Extract only recent information from 2024"
- "Include pricing in USD"
- "Summarize in bullet points"

---

### 5. Results Display

After extraction:
- Results appear in JSON format
- Syntax highlighted for readability
- Copy/paste friendly
- Includes metadata (source URL, provider used, model)

---

## Complete Workflow Example

### Extracting Company Information

1. **Configure Provider**
   - Select: `anthropic`
   - Model: `claude-3-sonnet-20240229`
   - Click "Save Config"

2. **Enter URL**
   - Click "URL" tab (if not selected)
   - Enter: `https://www.company-example.com/about`

3. **Select Schema**
   - Click "Business Info" button
   - Schema auto-loads with company fields

4. **Add Instructions** (optional)
   ```
   Focus on founding information and key executives
   ```

5. **Extract**
   - Click "Extract Data" button
   - Wait for results (shows loading spinner)

6. **Review Results**
   ```json
   {
     "company_name": "Example Corp",
     "industry": "Technology",
     "founded": "2010",
     "headquarters": "San Francisco, CA",
     "employees": "500-1000",
     "key_products": ["Product A", "Product B"],
     "_source": {
       "url": "https://www.company-example.com/about",
       "provider": "anthropic",
       "model": "claude-3-sonnet-20240229"
     }
   }
   ```

---

## Custom Schema Examples

### Extract Article Content
```json
{
  "title": {
    "type": "string",
    "description": "Article headline"
  },
  "author": {
    "type": "string",
    "description": "Author name"
  },
  "published_date": {
    "type": "string",
    "description": "Publication date"
  },
  "summary": {
    "type": "string",
    "description": "Brief summary in 2-3 sentences"
  },
  "main_points": {
    "type": "array",
    "description": "Key points as bullet list"
  },
  "categories": {
    "type": "array",
    "description": "Article topics/tags"
  }
}
```

### Extract Product Details
```json
{
  "product_name": {
    "type": "string",
    "description": "Product name"
  },
  "brand": {
    "type": "string",
    "description": "Brand or manufacturer"
  },
  "price": {
    "type": "string",
    "description": "Current price"
  },
  "rating": {
    "type": "string",
    "description": "Average customer rating"
  },
  "features": {
    "type": "array",
    "description": "Key product features"
  },
  "specifications": {
    "type": "object",
    "description": "Technical specs"
  }
}
```

### Extract Contact Information
```json
{
  "name": {
    "type": "string",
    "description": "Person or organization name"
  },
  "email": {
    "type": "string",
    "description": "Email address"
  },
  "phone": {
    "type": "string",
    "description": "Phone number"
  },
  "address": {
    "type": "string",
    "description": "Physical address"
  },
  "website": {
    "type": "string",
    "description": "Website URL"
  },
  "social_media": {
    "type": "object",
    "description": "Social media profiles"
  }
}
```

---

## Tips & Best Practices

### Provider Selection
- **OpenAI (GPT-4)** - Best for complex reasoning and detailed extraction
- **Anthropic (Claude)** - Excellent for longer content and nuanced understanding
- **Google (Gemini)** - Fast and cost-effective for simple extractions
- **Ollama** - Free local option, requires setup but no API costs

### Schema Design
- **Be specific** - Clear descriptions improve extraction accuracy
- **Keep it simple** - Start with fewer fields, add more as needed
- **Use examples** - Add example values in descriptions
- **Test iteratively** - Refine schema based on results

### Performance
- **URL mode** - May be slower due to web scraping
- **Text mode** - Fastest, direct extraction
- **Large content** - May timeout or truncate (100KB limit)

### Troubleshooting
- **"Provider test failed"** - Check API key in `.env` file
- **"Invalid JSON schema"** - Validate JSON syntax
- **"Request timeout"** - Try shorter content or simpler schema
- **"Error: 401"** - Invalid or missing API key

---

## API Endpoint Reference

For programmatic access:

### Extract Data
```bash
curl -X POST http://localhost:8000/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "schema_def": {
      "title": {"type": "string"}
    },
    "provider": "openai"
  }'
```

### List Providers
```bash
curl http://localhost:8000/api/providers
```

### Update Config
```bash
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{"provider": "anthropic", "model": "claude-3-opus-20240229"}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter` in text areas - Submit form
- `Tab` in schema editor - Proper JSON indentation
- `Ctrl/Cmd + A` in results - Select all for copying

---

## Support

For issues or questions:
- Check the main README.md
- Review .env.example for configuration
- Test providers individually using CLI: `python -m src.cli.main test-provider openai`

---

## Next Steps

- Set up multiple provider API keys for redundancy
- Create custom schema templates for your use cases
- Use CLI for batch processing multiple URLs
- Integrate API endpoints into your applications
