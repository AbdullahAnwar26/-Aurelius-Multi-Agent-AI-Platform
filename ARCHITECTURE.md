# System Architecture — Aurelius Backend

## High-Level Overview
┌─────────────┐
│   Client    │ (Frontend, Mobile, External API)
└──────┬──────┘
│ HTTP/REST
▼
┌──────────────────────────────┐
│   Django REST Framework      │
│  ┌──────────────────────┐    │
│  │  URL Router          │    │
│  ├──────────────────────┤    │
│  │  Authentication      │    │
│  │  - JWT (SimpleJWT)   │    │
│  │  - API Key           │    │
│  ├──────────────────────┤    │
│  │  ViewSets / Views    │    │
│  └──────────────────────┘    │
└──────────┬───────────────────┘
│
▼
┌──────────────────────────────┐
│  AI Gateway Service Layer    │
│  (ai_gateway.py)             │
└──────────┬───────────────────┘
│
▼
┌──────────────────────────────┐
│   CrewAI Agent Fleet         │
│  ┌──────────────────────┐    │
│  │  Root Orchestrator   │    │
│  │  (Aurelius)          │    │
│  └─────┬────────────────┘    │
│        │                      │
│  ┌─────┴──────────────────┐   │
│  │ 8 Specialized Agents:  │   │
│  │ • QnA Research         │   │
│  │ • Data Analysis        │   │
│  │ • Email Automation     │   │
│  │ • Stock Analysis       │   │
│  │ • Resume Optimizer     │   │
│  │ • Sentiment Analysis   │   │
│  │ • Talent Sourcing      │   │
│  │ • RAG Research         │   │
│  └────────────────────────┘   │
└──────────────────────────────┘
│
▼
┌──────────────────────────────┐
│   External Services          │
│  • Google Gemini 2.0 Flash   │
│  • Tavily Web Search         │
│  • GitHub API                │
│  • Alpha Vantage (stocks)    │
│  • ChromaDB (vector store)   │
└──────────────────────────────┘

## Request Flow

1. Client sends authenticated request to `/api/root-agent/` or `/api/agent/{name}/`
2. Django URL router matches path
3. Authentication backend validates JWT or API key
4. View extracts parameters, file uploads, conversation context
5. View calls `call_ai_agent(agent_type, query, file_path)`
6. Gateway lazy-imports the appropriate agent
7. Agent crew executes (may make multiple LLM calls, external API calls)
8. View stores result in database (ChatMessage, TokenLog)
9. CustomJSONRenderer wraps response in standard envelope
10. Response returned to client

## Data Flow
User Input
│
├─→ Validate & Parse (DRF serializers)
├─→ Check Permissions (Auth backends)
├─→ Save to Conversation (ChatMessage.sender='user')
│
├─→ Call Agent (AI Gateway)
│    ├─→ LLM thinks (Gemini)
│    ├─→ May call tools (search, GitHub, etc.)
│    └─→ Returns response
│
├─→ Save to Conversation (ChatMessage.sender='agent')
├─→ Log tokens used (TokenLog)
├─→ Format response
│
└─→ Return to Client

## Database Schema

See `models.py` for full schema. Key entities:

- **User** — custom user with email login
- **Agent** — registry of all available agents
- **Conversation** — chat session per user per agent
- **ChatMessage** — individual messages with sender, tokens, attachments
- **APIKey** — external access keys with per-agent permissions
- **TokenLog** — token usage tracking per message
- **RootAgentMemory** — routing decisions log

## Deployment Architecture
┌─────────────┐
│   GitHub    │ Push to main branch
└──────┬──────┘
│
▼
┌──────────────────┐
│   Render         │ Webhook trigger
│  ┌────────────┐  │
│  │ Build Step │  │ pip install -r requirements.txt
│  ├────────────┤  │
│  │ Migrate    │  │ python manage.py migrate
│  ├────────────┤  │
│  │ Collect    │  │ python manage.py collectstatic --noinput
│  ├────────────┤  │
│  │ Start      │  │ gunicorn myproject.wsgi ...
│  └────────────┘  │
└─────┬────────────┘
│
▼
┌──────────────────┐
│   Gunicorn       │ WSGI application server
│  ├─ Worker 1     │
│  ├─ Worker 2     │
│  └─ Worker 3     │
└─────┬────────────┘
│
▼
┌──────────────────┐
│   PostgreSQL     │ Neon (managed DB)
│  (read/write)    │
└──────────────────┘

## Performance Considerations

- **Connection pooling:** `CONN_MAX_AGE: 600` reuses DB connections
- **Static files:** Whitenoise serves compressed, fingerprinted CSS/JS
- **Gunicorn timeout:** `--timeout 120` allows agent calls to complete
- **Lazy imports:** Agent code only loaded when needed

See `README_BACKEND.md` for security and deployment details.