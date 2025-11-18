// Firecrawl LLM Extraction - Frontend JavaScript

let currentTab = 'url';

// Tab switching
function switchTab(tab) {
    currentTab = tab;

    // Update tab buttons
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');
}

// Provider configuration
async function updateProvider() {
    const provider = document.getElementById('provider').value;
    const modelInput = document.getElementById('model');

    // Fetch provider info to get default model
    try {
        const response = await fetch('/api/providers');
        const providers = await response.json();
        const selected = providers.find(p => p.name === provider);

        if (selected) {
            modelInput.placeholder = selected.default_model;
        }
    } catch (error) {
        console.error('Error fetching providers:', error);
    }
}

async function saveProviderConfig() {
    const provider = document.getElementById('provider').value;
    const model = document.getElementById('model').value || null;

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider, model })
        });

        const result = await response.json();

        if (result.success) {
            showStatus('provider-status', `Provider set to ${result.provider} (model: ${result.model})`, 'success');
        } else {
            showStatus('provider-status', 'Failed to update configuration', 'error');
        }
    } catch (error) {
        showStatus('provider-status', `Error: ${error.message}`, 'error');
    }
}

async function testProvider() {
    const provider = document.getElementById('provider').value;
    const model = document.getElementById('model').value || null;

    showStatus('provider-status', 'Testing provider...', '');

    try {
        const response = await fetch(`/api/test-provider?provider=${provider}${model ? `&model=${model}` : ''}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            showStatus('provider-status', `Provider ${provider} is working correctly!`, 'success');
        } else {
            showStatus('provider-status', `Test failed: ${result.error}`, 'error');
        }
    } catch (error) {
        showStatus('provider-status', `Error: ${error.message}`, 'error');
    }
}

function showStatus(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = 'status-message ' + type;
}

// Extraction
async function performExtraction() {
    const schemaText = document.getElementById('schema-input').value;
    const instructions = document.getElementById('instructions-input').value || null;

    // Parse schema
    let schema;
    try {
        schema = JSON.parse(schemaText);
    } catch (error) {
        alert('Invalid JSON schema: ' + error.message);
        return;
    }

    // Build request based on current tab
    const request = {
        schema_def: schema,
        instructions: instructions
    };

    switch (currentTab) {
        case 'url':
            request.url = document.getElementById('url-input').value;
            if (!request.url) {
                alert('Please enter a URL');
                return;
            }
            break;
        case 'text':
            request.text = document.getElementById('text-input').value;
            if (!request.text) {
                alert('Please enter text content');
                return;
            }
            break;
        case 'html':
            request.html = document.getElementById('html-input').value;
            if (!request.html) {
                alert('Please enter HTML content');
                return;
            }
            break;
    }

    // Show loading
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('results').textContent = '';

    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('results').textContent = JSON.stringify(result.data, null, 2);
        } else {
            document.getElementById('results').textContent = `Error: ${result.error}`;
        }
    } catch (error) {
        document.getElementById('results').textContent = `Error: ${error.message}`;
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

// Example schemas
const exampleSchemas = {
    business: {
        company_name: { type: "string", description: "Company name" },
        industry: { type: "string", description: "Industry/sector" },
        description: { type: "string", description: "Brief company description" },
        founded: { type: "string", description: "Year founded" },
        headquarters: { type: "string", description: "HQ location" },
        employees: { type: "string", description: "Number of employees" },
        website: { type: "string", description: "Website URL" },
        key_products: { type: "array", description: "Main products/services" }
    },
    article: {
        title: { type: "string", description: "Article title" },
        author: { type: "string", description: "Author name" },
        publication_date: { type: "string", description: "Publication date" },
        summary: { type: "string", description: "Article summary" },
        main_points: { type: "array", description: "Main points discussed" },
        topics: { type: "array", description: "Topics/categories" }
    },
    product: {
        name: { type: "string", description: "Product name" },
        brand: { type: "string", description: "Brand name" },
        price: { type: "string", description: "Price" },
        description: { type: "string", description: "Product description" },
        features: { type: "array", description: "Key features" },
        specifications: { type: "object", description: "Technical specifications" },
        rating: { type: "string", description: "Average rating" }
    },
    contact: {
        name: { type: "string", description: "Person/company name" },
        email: { type: "string", description: "Email address" },
        phone: { type: "string", description: "Phone number" },
        address: { type: "string", description: "Physical address" },
        social_media: { type: "object", description: "Social media links" }
    }
};

function loadExample(type) {
    const schema = exampleSchemas[type];
    if (schema) {
        document.getElementById('schema-input').value = JSON.stringify(schema, null, 2);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateProvider();
});
