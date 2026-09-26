# Flask Free AI API

A lightweight Flask API that accepts a prompt and routes it through multiple AI providers with automatic fallback handling.

## Features

- Flask REST endpoint for AI requests
- Required input validation
- Provider fallback chain:
  - Gemini
  - Cloudflare
  - Qwen
  - Groq
  - Random/LLM7
  - Local mock fallback
- Environment-based API key configuration via `.env`
- Health check endpoint

## Project structure

- `main.py` - Flask app entry point
- `ai_script.py` - AI provider logic and fallback functions
- `.env` - local environment variables

## Requirements

Install the dependencies:

```bash
pip install flask python-dotenv requests google-genai openai
```

## Environment setup

Create a `.env` file in the project root with your API keys:

```env
GEMINI_API_KEY=your_key_here
CLOUDFLARE_ACC_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_token_here
ORCA_ROUTER_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
LLM7IO_API_KEY=your_key_here
```

## Run the app

```bash
python main.py
```

The app will run on:

```text
http://localhost:5000
```

## Endpoints

### Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### AI request

```http
POST /api/v1/ai
Content-Type: application/json
```

Required JSON body:

```json
{
  "prompt": "Hello there",
  "context": "Some context for the conversation",
  "history": "Previous messages",
  "system_command": "You are a helpful assistant."
}
```

Optional field:

```json
{
  "provider": "gemini"
}
```

Example response:

```json
{
  "success": true,
  "provider": "cloudflare",
  "response": "Hello! How can I help you today?"
}
```

## Example with curl

```bash
curl -X POST http://localhost:5000/api/v1/ai \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to reverse a string",
    "context": "No context",
    "history": "No history",
    "system_command": "You are a helpful coding assistant."
  }'
```

## Notes

- If a provider fails or a key is missing, the app automatically tries the next provider.
- If all providers fail, it returns a clear error response instead of crashing.
- The API is intentionally simple and easy to extend for your own app or frontend integration.
