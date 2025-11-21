# 🚀 Quick Start Guide

## Start the Web UI in 3 Steps

### 1. Setup (One-time)
```bash
# Clone the repository
git clone https://github.com/Maws7140/Business-Data-Extraction-workflow.git
cd Business-Data-Extraction-workflow

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use any text editor
```

Add at least one API key:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### 2. Launch
```bash
# Linux/Mac
./start-ui.sh

# Windows
start-ui.bat

# Or manually
python -m src.cli.main serve
```

### 3. Open Browser
Navigate to: **http://localhost:8000**

---

## Your First Extraction (60 seconds)

### Example: Extract Company Information

1. **Configure Provider**
   ```
   Provider: [Select "Anthropic"] ▼
   Model: [Leave default or enter custom]
   [Save Config]
   ```

2. **Enter URL**
   ```
   URL Tab: https://www.anthropic.com
   ```

3. **Use Example Schema**
   ```
   Click: [Business Info] button
   ```
   This auto-fills the schema with company fields.

4. **Extract**
   ```
   Click: [Extract Data]
   ```

5. **View Results**
   ```json
   {
     "company_name": "Anthropic",
     "industry": "Artificial Intelligence",
     "description": "...",
     "headquarters": "San Francisco, CA",
     ...
   }
   ```

Done! 🎉

---

## Web UI Layout

```
┌─────────────────────────────────────────────────┐
│  🔥 Firecrawl LLM Extraction                    │
│  Extract structured data from any URL using AI  │
├─────────────────────────────────────────────────┤
│  ⚙️ LLM Provider Configuration                  │
│  ┌──────────┐ ┌─────────┐                       │
│  │ Provider ▼│ │  Model  │ [Save] [Test]       │
│  └──────────┘ └─────────┘                       │
├─────────────────────────────────────────────────┤
│  📝 Data Extraction                             │
│  [URL] [Text] [HTML]  ← Choose input type       │
│                                                  │
│  URL: [https://example.com           ]          │
│                                                  │
│  Schema (JSON):                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ {                                        │   │
│  │   "title": {"type": "string", ...}      │   │
│  │   "summary": {"type": "string", ...}    │   │
│  │ }                                        │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  Instructions (optional):                       │
│  [Focus on recent information...        ]       │
│                                                  │
│  [        Extract Data        ]  ← Click!       │
├─────────────────────────────────────────────────┤
│  📊 Results                                     │
│  ┌─────────────────────────────────────────┐   │
│  │ {                                        │   │
│  │   "title": "Page Title",                │   │
│  │   "summary": "...",                     │   │
│  │   ...                                   │   │
│  │ }                                        │   │
│  └─────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  📋 Example Schemas                             │
│  [Business] [Article] [Product] [Contact]      │
└─────────────────────────────────────────────────┘
```

---

## Features Checklist

- ✅ **4 AI Providers**: OpenAI, Anthropic, Google, Ollama
- ✅ **Switch Anytime**: Change providers with dropdown
- ✅ **3 Input Modes**: URL, Text, HTML
- ✅ **Schema Templates**: Pre-built examples
- ✅ **Custom Schemas**: Define your own JSON structure
- ✅ **Live Testing**: Test providers before extraction
- ✅ **Real-time Results**: Formatted JSON output
- ✅ **No Code Required**: Point-and-click interface

---

## Common Use Cases

### 🏢 Business Research
Extract company information from corporate websites
```
Schema: Business Info
Provider: Anthropic (best for detailed analysis)
```

### 📰 Content Analysis
Extract article details from news sites
```
Schema: Article
Provider: OpenAI (excellent for summarization)
```

### 🛒 E-commerce Data
Extract product information from stores
```
Schema: Product
Provider: Google Gemini (fast and cost-effective)
```

### 📞 Contact Extraction
Extract contact details from pages
```
Schema: Contact Info
Provider: Any (simple extraction)
```

---

## Provider Comparison

| Provider | Best For | Speed | Cost | Context |
|----------|----------|-------|------|---------|
| **OpenAI** | Complex reasoning | Fast | $$$ | 128K |
| **Anthropic** | Long content, accuracy | Medium | $$ | 200K |
| **Google** | Simple tasks, speed | Very Fast | $ | 32K |
| **Ollama** | Privacy, offline | Slow | Free | Varies |

**Recommendation:** Start with Google Gemini for testing, upgrade to Anthropic Claude for production.

---

## Troubleshooting

### "Provider test failed"
→ Check your API key in `.env` file

### "Invalid JSON schema"
→ Use the example schemas as templates

### "Request timeout"
→ Try with shorter content or simpler schema

### "Connection refused"
→ Make sure server is running: `./start-ui.sh`

---

## Next Steps

1. ✅ Start the Web UI
2. ✅ Test with example URL
3. 📚 Read [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for advanced features
4. 💡 Check [EXAMPLES.md](EXAMPLES.md) for real-world use cases
5. ⚡ Try CLI for batch processing: `python -m src.cli.main --help`

---

## Need Help?

- 📖 **Full Documentation**: [README.md](README.md)
- 🎯 **Web UI Guide**: [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)
- 💡 **Examples**: [EXAMPLES.md](EXAMPLES.md)
- 💬 **Issues**: [GitHub Issues](https://github.com/Maws7140/Business-Data-Extraction-workflow/issues)

---

## Pro Tips

💡 **Save API costs**: Use Ollama for development/testing

💡 **Better accuracy**: Write detailed schema descriptions

💡 **Faster extraction**: Use Text mode instead of URL mode when possible

💡 **Batch processing**: Use CLI for multiple URLs

💡 **Compare results**: Try same extraction with different providers
