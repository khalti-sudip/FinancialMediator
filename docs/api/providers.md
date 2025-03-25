# Providers API Documentation

This document describes the API endpoints for managing payment providers, API keys, and webhooks.

## Table of Contents
- [Provider Management](#provider-management)
- [API Key Management](#api-key-management)
- [Webhook Management](#webhook-management)

## Provider Management

### List Providers
```http
GET /api/v1/providers/
```

List all available providers with optional filtering.

**Query Parameters:**
- `type` (string): Filter by provider type (payment, wallet, bank, kyc)
- `status` (string): Filter by status (active, maintenance, offline)
- `active` (boolean): Filter by active state

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "name": "Test Provider",
            "code": "TEST",
            "provider_type": "payment",
            "supported_currencies": ["USD", "EUR"],
            "supported_countries": ["US", "GB"],
            "is_active": true,
            "status": "active",
            "api_base_url": "https://api.test.com",
            "api_version": "v1",
            "webhook_url": "https://webhook.test.com",
            "rate_limit": 1000,
            "concurrent_requests": 10,
            "created_at": "2025-03-25T13:06:22Z",
            "updated_at": "2025-03-25T13:06:22Z",
            "last_check_at": "2025-03-25T13:06:22Z"
        }
    ]
}
```

### Create Provider
```http
POST /api/v1/providers/
```

Create a new payment provider.

**Request Body:**
```json
{
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
}
```

### Get Provider Details
```http
GET /api/v1/providers/{id}/
```

Get detailed information about a specific provider.

**Response:**
```json
{
    "id": "uuid",
    "name": "Test Provider",
    "code": "TEST",
    "provider_type": "payment",
    "supported_currencies": ["USD", "EUR"],
    "supported_countries": ["US", "GB"],
    "is_active": true,
    "status": "active",
    "api_base_url": "https://api.test.com",
    "api_version": "v1",
    "webhook_url": "https://webhook.test.com",
    "rate_limit": 1000,
    "concurrent_requests": 10,
    "settings": {
        "success_url": "https://success.test.com",
        "cancel_url": "https://cancel.test.com",
        "webhook_events": ["payment.success", "payment.failure"]
    },
    "created_at": "2025-03-25T13:06:22Z",
    "updated_at": "2025-03-25T13:06:22Z",
    "last_check_at": "2025-03-25T13:06:22Z"
}
```

### Check Provider Status
```http
POST /api/v1/providers/{id}/check_status/
```

Check the current status of a provider.

**Response:**
```json
{
    "status": "active",
    "is_healthy": true,
    "last_check": "2025-03-25T13:06:22Z"
}
```

### Update Provider Status
```http
POST /api/v1/providers/{id}/update_status/
```

Update the status of a provider.

**Request Body:**
```json
{
    "status": "maintenance",
    "message": "Scheduled maintenance",
    "metadata": {
        "start_time": "2025-03-25T14:00:00Z",
        "duration": 3600
    }
}
```

### Get Provider Statistics
```http
GET /api/v1/providers/{id}/statistics/
```

Get usage statistics for a provider.

**Response:**
```json
{
    "total_requests": 1000,
    "success_rate": 0.99,
    "average_response_time": 150.5,
    "error_rate": 0.01,
    "active_keys": 5,
    "webhook_success_rate": 0.98,
    "last_update": "2025-03-25T13:06:22Z"
}
```

## API Key Management

### List API Keys
```http
GET /api/v1/provider-keys/
```

List all API keys with optional filtering.

**Query Parameters:**
- `provider` (uuid): Filter by provider ID
- `environment` (string): Filter by environment (test, prod)
- `active` (boolean): Filter by active state
- `user` (uuid): Filter by user ID

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "key_id": "test_key",
            "provider": "uuid",
            "is_active": true,
            "environment": "test",
            "user": "uuid",
            "daily_limit": 1000,
            "monthly_limit": 30000,
            "created_at": "2025-03-25T13:06:22Z",
            "expires_at": "2026-03-25T13:06:22Z",
            "last_used_at": "2025-03-25T13:06:22Z"
        }
    ]
}
```

### Create API Key
```http
POST /api/v1/provider-keys/
```

Create a new API key.

**Request Body:**
```json
{
    "provider": "uuid",
    "user": "uuid",
    "environment": "test",
    "daily_limit": 1000,
    "monthly_limit": 30000
}
```

**Response:**
```json
{
    "id": "uuid",
    "key_id": "test_key",
    "key_secret": "secret_key",  // Only shown on creation
    "provider": "uuid",
    "is_active": true,
    "environment": "test",
    "user": "uuid",
    "daily_limit": 1000,
    "monthly_limit": 30000,
    "created_at": "2025-03-25T13:06:22Z",
    "expires_at": "2026-03-25T13:06:22Z"
}
```

### Deactivate API Key
```http
POST /api/v1/provider-keys/{id}/deactivate/
```

Deactivate an API key.

**Response:**
```json
{
    "message": "Key deactivated successfully"
}
```

### Get API Key Usage
```http
GET /api/v1/provider-keys/{id}/usage/
```

Get usage statistics for an API key.

**Response:**
```json
{
    "daily_usage": 500,
    "monthly_usage": 15000,
    "daily_remaining": 500,
    "monthly_remaining": 15000,
    "last_used": "2025-03-25T13:06:22Z"
}
```

## Webhook Management

### List Webhooks
```http
GET /api/v1/provider-webhooks/
```

List all webhooks with optional filtering.

**Query Parameters:**
- `provider` (uuid): Filter by provider ID
- `event_type` (string): Filter by event type
- `status` (string): Filter by status
- `start_date` (string): Filter by start date
- `end_date` (string): Filter by end date

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "event_id": "evt_123",
            "provider": "uuid",
            "event_type": "payment.success",
            "event_data": {
                "transaction_id": "tx_123",
                "amount": 100
            },
            "status": "completed",
            "error_message": null,
            "retry_count": 0,
            "ip_address": "127.0.0.1",
            "headers": {
                "User-Agent": "Test"
            },
            "created_at": "2025-03-25T13:06:22Z",
            "processed_at": "2025-03-25T13:06:22Z"
        }
    ]
}
```

### Create Webhook
```http
POST /api/v1/provider-webhooks/
```

Create a new webhook event.

**Request Body:**
```json
{
    "provider": "uuid",
    "event_type": "payment.success",
    "event_data": {
        "transaction_id": "tx_123",
        "amount": 100
    },
    "signature": "test_signature",
    "ip_address": "127.0.0.1",
    "headers": {
        "User-Agent": "Test"
    }
}
```

### Retry Webhook
```http
POST /api/v1/provider-webhooks/{id}/retry/
```

Retry processing a failed webhook.

**Response:**
```json
{
    "message": "Webhook retry initiated"
}
```

### Cancel Webhook
```http
POST /api/v1/provider-webhooks/{id}/cancel/
```

Cancel a pending webhook.

**Response:**
```json
{
    "message": "Webhook cancelled successfully"
}
```

### Get Webhook Summary
```http
GET /api/v1/provider-webhooks/summary/
```

Get webhook processing summary.

**Response:**
```json
{
    "total": 1000,
    "completed": 980,
    "failed": 15,
    "pending": 5,
    "success_rate": 0.98,
    "time_range": {
        "start": "2025-03-24T13:06:22Z",
        "end": "2025-03-25T13:06:22Z"
    }
}
```
