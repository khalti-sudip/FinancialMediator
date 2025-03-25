# Provider API Examples

This document provides example usage of the Providers API using various programming languages and tools.

## Python Examples

### Create a Provider
```python
import requests
import json

# API configuration
API_URL = "https://api.example.com/v1"
API_KEY = "your_api_key"

# Provider data
provider_data = {
    "name": "Stripe",
    "code": "STRIPE",
    "provider_type": "payment",
    "supported_currencies": ["USD", "EUR", "GBP"],
    "supported_countries": ["US", "GB", "EU"],
    "api_base_url": "https://api.stripe.com",
    "api_version": "2022-11-15",
    "webhook_url": "https://webhooks.stripe.com",
    "rate_limit": 100,
    "concurrent_requests": 5,
    "settings": {
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
        "webhook_events": [
            "payment.success",
            "payment.failure",
            "refund.created"
        ]
    }
}

# Create provider
response = requests.post(
    f"{API_URL}/providers/",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    data=json.dumps(provider_data)
)

print(response.json())
```

### Generate API Key
```python
import requests

# API configuration
API_URL = "https://api.example.com/v1"
API_KEY = "your_api_key"

# Key data
key_data = {
    "provider": "provider_id",
    "environment": "test",
    "daily_limit": 1000,
    "monthly_limit": 30000
}

# Create API key
response = requests.post(
    f"{API_URL}/provider-keys/",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json=key_data
)

print(response.json())
```

### Process Webhook
```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)

WEBHOOK_SECRET = "your_webhook_secret"

def verify_signature(payload_body, signature):
    """Verify webhook signature."""
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature.encode(), expected.encode())

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    """Handle provider webhook."""
    # Get signature
    signature = request.headers.get("X-Provider-Signature")
    if not signature:
        return jsonify({"error": "No signature"}), 400
    
    # Verify signature
    payload_body = request.get_data()
    if not verify_signature(payload_body, signature):
        return jsonify({"error": "Invalid signature"}), 400
    
    # Parse event data
    event_data = json.loads(payload_body)
    
    # Handle event
    event_type = event_data.get("type")
    if event_type == "payment.success":
        handle_payment_success(event_data)
    elif event_type == "payment.failure":
        handle_payment_failure(event_data)
    
    return jsonify({"received": True})

if __name__ == "__main__":
    app.run(port=5000)
```

## JavaScript Examples

### Create a Provider
```javascript
const axios = require('axios');

// API configuration
const API_URL = 'https://api.example.com/v1';
const API_KEY = 'your_api_key';

// Provider data
const providerData = {
    name: 'PayPal',
    code: 'PAYPAL',
    provider_type: 'payment',
    supported_currencies: ['USD', 'EUR'],
    supported_countries: ['US', 'GB'],
    api_base_url: 'https://api.paypal.com',
    api_version: 'v1',
    webhook_url: 'https://webhooks.paypal.com',
    rate_limit: 100,
    concurrent_requests: 5,
    settings: {
        success_url: 'https://example.com/success',
        cancel_url: 'https://example.com/cancel',
        webhook_events: ['payment.success', 'payment.failure']
    }
};

// Create provider
async function createProvider() {
    try {
        const response = await axios.post(
            `${API_URL}/providers/`,
            providerData,
            {
                headers: {
                    'Authorization': `Bearer ${API_KEY}`,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        console.log(response.data);
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}

createProvider();
```

### Handle Webhooks
```javascript
const express = require('express');
const crypto = require('crypto');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.raw({ type: 'application/json' }));

const WEBHOOK_SECRET = 'your_webhook_secret';

function verifySignature(payload, signature) {
    const expectedSignature = crypto
        .createHmac('sha256', WEBHOOK_SECRET)
        .update(payload)
        .digest('hex');
    
    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSignature)
    );
}

app.post('/webhook', (req, res) => {
    // Get signature
    const signature = req.headers['x-provider-signature'];
    if (!signature) {
        return res.status(400).json({ error: 'No signature' });
    }
    
    // Verify signature
    const payload = req.body;
    if (!verifySignature(payload, signature)) {
        return res.status(400).json({ error: 'Invalid signature' });
    }
    
    // Parse event data
    const eventData = JSON.parse(payload);
    
    // Handle event
    switch (eventData.type) {
        case 'payment.success':
            handlePaymentSuccess(eventData);
            break;
        case 'payment.failure':
            handlePaymentFailure(eventData);
            break;
    }
    
    res.json({ received: true });
});

app.listen(3000, () => {
    console.log('Webhook server running on port 3000');
});
```

## cURL Examples

### List Providers
```bash
curl -X GET "https://api.example.com/v1/providers/" \
    -H "Authorization: Bearer your_api_key" \
    -H "Content-Type: application/json"
```

### Create Provider
```bash
curl -X POST "https://api.example.com/v1/providers/" \
    -H "Authorization: Bearer your_api_key" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test Provider",
        "code": "TEST",
        "provider_type": "payment",
        "supported_currencies": ["USD", "EUR"],
        "supported_countries": ["US", "GB"],
        "api_base_url": "https://api.test.com",
        "api_version": "v1",
        "webhook_url": "https://webhook.test.com",
        "rate_limit": 1000,
        "concurrent_requests": 10,
        "settings": {
            "success_url": "https://success.test.com",
            "cancel_url": "https://cancel.test.com",
            "webhook_events": ["payment.success", "payment.failure"]
        }
    }'
```

### Check Provider Status
```bash
curl -X POST "https://api.example.com/v1/providers/{id}/check_status/" \
    -H "Authorization: Bearer your_api_key" \
    -H "Content-Type: application/json"
```

### Create API Key
```bash
curl -X POST "https://api.example.com/v1/provider-keys/" \
    -H "Authorization: Bearer your_api_key" \
    -H "Content-Type: application/json" \
    -d '{
        "provider": "provider_id",
        "environment": "test",
        "daily_limit": 1000,
        "monthly_limit": 30000
    }'
```

### Get Webhook Summary
```bash
curl -X GET "https://api.example.com/v1/provider-webhooks/summary/" \
    -H "Authorization: Bearer your_api_key" \
    -H "Content-Type: application/json"
```
