# Usage Examples

## Example 1: Extract Company Information from Website

### Input
**URL:** `https://www.anthropic.com`

**Schema:**
```json
{
  "company_name": {
    "type": "string",
    "description": "Company name"
  },
  "industry": {
    "type": "string",
    "description": "Primary industry"
  },
  "description": {
    "type": "string",
    "description": "Company description"
  },
  "products": {
    "type": "array",
    "description": "Main products or services"
  }
}
```

**Provider:** `anthropic` (Claude 3 Sonnet)

### CLI Command
```bash
python -m src.cli.main extract "https://www.anthropic.com" \
  --provider anthropic \
  --schema '{"company_name":"string","industry":"string","description":"string","products":"array"}'
```

### Expected Output
```json
{
  "company_name": "Anthropic",
  "industry": "Artificial Intelligence",
  "description": "AI safety and research company focused on developing reliable, interpretable, and steerable AI systems",
  "products": ["Claude", "Constitutional AI", "AI Safety Research"],
  "_source": {
    "url": "https://www.anthropic.com",
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229"
  }
}
```

---

## Example 2: Extract Article Content

### Input
**Text:**
```
Breaking News: New AI Model Released

San Francisco, CA - January 15, 2024

Tech company XYZ Corp announced today the release of their latest AI model,
SuperAI 2.0, which shows significant improvements in natural language understanding.
The model was trained on diverse datasets and achieves state-of-the-art results
on multiple benchmarks.

Key features include improved reasoning capabilities, multilingual support,
and enhanced safety measures. The model will be available via API starting next month.
```

**Schema:**
```json
{
  "headline": {
    "type": "string",
    "description": "Article headline"
  },
  "location": {
    "type": "string",
    "description": "Location mentioned"
  },
  "date": {
    "type": "string",
    "description": "Publication date"
  },
  "company": {
    "type": "string",
    "description": "Company mentioned"
  },
  "product_name": {
    "type": "string",
    "description": "Product or model name"
  },
  "key_features": {
    "type": "array",
    "description": "Main features listed"
  },
  "availability": {
    "type": "string",
    "description": "When product will be available"
  }
}
```

### CLI Command
```bash
echo "Breaking News: New AI Model Released..." > article.txt

python -m src.cli.main extract-text article.txt \
  --provider openai \
  --schema schema.json
```

### Expected Output
```json
{
  "headline": "Breaking News: New AI Model Released",
  "location": "San Francisco, CA",
  "date": "January 15, 2024",
  "company": "XYZ Corp",
  "product_name": "SuperAI 2.0",
  "key_features": [
    "Improved reasoning capabilities",
    "Multilingual support",
    "Enhanced safety measures"
  ],
  "availability": "Next month via API",
  "_source": {
    "provider": "openai",
    "model": "gpt-4-turbo-preview"
  }
}
```

---

## Example 3: Extract Product Details from E-commerce

### Input (Web UI)
**URL:** E-commerce product page

**Schema:**
```json
{
  "product_name": {
    "type": "string",
    "description": "Product name"
  },
  "brand": {
    "type": "string",
    "description": "Brand name"
  },
  "price": {
    "type": "string",
    "description": "Current price"
  },
  "original_price": {
    "type": "string",
    "description": "Original price if on sale"
  },
  "rating": {
    "type": "string",
    "description": "Average customer rating"
  },
  "reviews_count": {
    "type": "string",
    "description": "Number of reviews"
  },
  "features": {
    "type": "array",
    "description": "Key product features"
  },
  "specifications": {
    "type": "object",
    "description": "Technical specifications"
  },
  "in_stock": {
    "type": "string",
    "description": "Availability status"
  }
}
```

**Instructions:** "Extract pricing in USD. Include all technical specifications."

---

## Example 4: Batch Extract Contact Information

### Input
**urls.txt:**
```
https://company1.com/contact
https://company2.com/about
https://company3.com/team
```

**Schema (contact_schema.json):**
```json
{
  "organization": {
    "type": "string",
    "description": "Organization name"
  },
  "email": {
    "type": "string",
    "description": "Contact email"
  },
  "phone": {
    "type": "string",
    "description": "Phone number"
  },
  "address": {
    "type": "string",
    "description": "Physical address"
  },
  "social_media": {
    "type": "object",
    "description": "Social media links (Twitter, LinkedIn, etc)"
  }
}
```

### CLI Command
```bash
python -m src.cli.main batch urls.txt \
  --schema contact_schema.json \
  --provider google \
  --output contacts.json
```

### Expected Output (contacts.json)
```json
[
  {
    "organization": "Company 1",
    "email": "contact@company1.com",
    "phone": "+1-555-0101",
    "address": "123 Main St, City, State 12345",
    "social_media": {
      "twitter": "https://twitter.com/company1",
      "linkedin": "https://linkedin.com/company/company1"
    },
    "_source": {
      "url": "https://company1.com/contact",
      "provider": "google",
      "model": "gemini-pro"
    }
  },
  {
    "organization": "Company 2",
    "email": "info@company2.com",
    "phone": "+1-555-0102",
    "address": "456 Oak Ave, City, State 67890",
    "social_media": {
      "twitter": "https://twitter.com/company2",
      "linkedin": "https://linkedin.com/company/company2"
    },
    "_source": {
      "url": "https://company2.com/about",
      "provider": "google",
      "model": "gemini-pro"
    }
  }
]
```

---

## Example 5: Switching Providers on the Fly

### Scenario: Try multiple providers for best results

```bash
# Try with OpenAI
python -m src.cli.main extract "https://example.com" \
  --provider openai \
  --schema schema.json \
  --output openai_result.json

# Try with Anthropic
python -m src.cli.main extract "https://example.com" \
  --provider anthropic \
  --schema schema.json \
  --output anthropic_result.json

# Try with Google
python -m src.cli.main extract "https://example.com" \
  --provider google \
  --schema schema.json \
  --output google_result.json

# Compare results
diff openai_result.json anthropic_result.json
```

---

## Example 6: Using Ollama (Local/Free)

### Setup Ollama
```bash
# Install Ollama (see https://ollama.ai)
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
```

### Extract with Ollama
```bash
python -m src.cli.main extract "https://example.com" \
  --provider ollama \
  --model llama2 \
  --schema schema.json
```

**Note:** Ollama runs locally, so:
- No API costs
- Complete privacy
- May be slower than cloud APIs
- Requires local GPU/CPU resources

---

## Example 7: Complex Nested Schema

### Use Case: Extract structured company data with nested information

```json
{
  "company": {
    "name": {
      "type": "string",
      "description": "Company name"
    },
    "founded": {
      "type": "string",
      "description": "Year founded"
    },
    "headquarters": {
      "type": "object",
      "description": "HQ location with city, state, country"
    }
  },
  "executives": {
    "type": "array",
    "description": "List of key executives with name and title"
  },
  "financials": {
    "revenue": {
      "type": "string",
      "description": "Annual revenue"
    },
    "employees": {
      "type": "string",
      "description": "Number of employees"
    },
    "funding": {
      "type": "string",
      "description": "Total funding raised"
    }
  },
  "products": {
    "type": "array",
    "description": "Main products with name and description"
  }
}
```

---

## Example 8: Web UI Workflow

### Step-by-Step

1. **Start Server**
   ```bash
   ./start-ui.sh
   ```

2. **Open Browser**
   - Navigate to http://localhost:8000

3. **Configure Provider**
   - Select: `Anthropic`
   - Model: `claude-3-sonnet-20240229`
   - Click "Save Config"
   - Click "Test Provider" ✓

4. **Choose Input Type**
   - Click "URL" tab

5. **Enter URL**
   ```
   https://news.ycombinator.com
   ```

6. **Load Example Schema**
   - Click "Article" button (pre-fills schema)

7. **Customize Schema** (optional)
   - Edit JSON in schema editor

8. **Add Instructions**
   ```
   Focus on the top 3 stories only
   ```

9. **Extract**
   - Click "Extract Data" button
   - Wait for results

10. **Review & Copy**
    - Results appear in formatted JSON
    - Copy to clipboard or save

---

## Tips for Better Results

### Schema Design
✅ **Good:**
```json
{
  "price": {
    "type": "string",
    "description": "Current price in USD format ($XX.XX)"
  }
}
```

❌ **Too Vague:**
```json
{
  "price": "string"
}
```

### Provider Selection
- **Complex extraction** → Anthropic Claude or OpenAI GPT-4
- **Simple extraction** → Google Gemini or Ollama
- **Long content** → Anthropic Claude (200K context)
- **Cost-effective** → Google Gemini or Ollama
- **Offline/Private** → Ollama

### Instructions
✅ **Specific:**
```
Extract only products launched in 2024.
Include pricing in USD.
Format dates as YYYY-MM-DD.
```

❌ **Generic:**
```
Get the information
```

---

## Troubleshooting Common Issues

### Issue: Empty or incomplete results
**Solution:**
- Make schema descriptions more specific
- Add detailed instructions
- Try a different provider (Claude is best for complex extraction)

### Issue: JSON parsing errors
**Solution:**
- Simplify schema structure
- Avoid deeply nested objects
- Test with smaller content first

### Issue: Timeout errors
**Solution:**
- Content may be too long (100KB limit)
- Try Text mode instead of URL mode
- Break into smaller chunks

### Issue: Provider test fails
**Solution:**
- Check API key in `.env` file
- Verify API key is active/funded
- Check internet connection
- For Ollama: ensure service is running (`ollama serve`)
