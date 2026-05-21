<div align="center">

# 🤖 Aurelius — Multi-Agent AI Platform

### Backend Engineering Deep-Dive

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.16-ff1709?style=flat-square)](https://django-rest-framework.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.3-FF6B6B?style=flat-square)](https://crewai.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Render](https://img.shields.io/badge/Deployed-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://render.com)

> A production-deployed Django REST API that routes user requests to a fleet of 8 specialized CrewAI agents via a central orchestrator. Built with a focus on clean architecture, security, and real-world deployment practices.

</div>

---

## Table of Contents

- [Project Overview](#-project-overview)
- [Backend Architecture](#-backend-architecture)
- [API Design](#-api-design)
- [Authentication & Authorization](#-authentication--authorization)
- [Data Models](#-data-models)
- [The AI Gateway Layer](#-the-ai-gateway-layer)
- [Custom Middleware & Response Standardization](#-custom-middleware--response-standardization)
- [Security Implementation](#-security-implementation)
- [Deployment](#-deployment--production-setup)
- [Local Setup](#-local-development-setup)
- [Collaboration Guide](#-collaboration-guide)
- [API Reference](#-api-reference)

---

## 📌 Project Overview

Aurelius is a **Django REST Framework** backend that exposes a clean, authenticated REST API on top of a multi-agent AI system. The core challenge this project solves is providing a **single, stable API surface** that can route a request to any of 8 completely different AI agent pipelines — each with its own tools, LLMs, and file-handling logic — without exposing that complexity to the client.

**Core backend responsibilities this project demonstrates:**

- Designing and implementing a layered REST API with DRF
- Custom authentication backends (JWT + API Key in parallel)
- Fine-grained, attribute-based access control on API keys
- Normalized JSON response envelope across all endpoints
- Custom exception handling with consistent error shapes
- File upload handling and safe temp file lifecycle management
- Persistent conversation and message storage with relational models
- Production deployment with Gunicorn, Whitenoise, and PostgreSQL on Render

---

## 🏗️ Backend Architecture

The backend is organized into clear, separated layers. Each layer has one job.

```
Request
  │
  ▼
┌─────────────────────────────────────────────────────┐
│              URL Router  (myapp/urls.py)             │
│   DRF DefaultRouter (ModelViewSets) +               │
│   Manual path() declarations (custom views)         │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│         Authentication Middleware Layer              │
│                                                      │
│  1. JWTAuthentication  (SimpleJWT)                  │
│     └─ Validates Bearer token → sets request.user   │
│                                                      │
│  2. APIKeyAuthentication  (custom backend)          │
│     └─ Validates sk_* token → sets request.user     │
│        AND attaches request.api_key for ACL checks  │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              View Layer  (myapp/views.py)            │
│                                                      │
│  APIView subclasses   →  custom business logic      │
│  ModelViewSet         →  standard CRUD endpoints    │
│  generics.*           →  list/retrieve shortcuts    │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│           AI Gateway Service Layer                   │
│         (myapp/services/ai_gateway.py)               │
│                                                      │
│   call_ai_agent(agent_type, query, file_path)       │
│   └─ Lazy-imports and dispatches to the right crew  │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│               CrewAI Agent Fleet                     │
│  (myapp/ai/agents/*)                                 │
│                                                      │
│  Root Orchestrator → routes to one or many:         │
│  QnA · Data Analysis · Automation · Stock           │
│  Resume Optimizer · Sentiment · Talent · RAG        │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│         Response Renderer  (CustomJSONRenderer)      │
│   Wraps ALL responses in standard envelope:         │
│   { "meta": {}, "message": "...", "error": bool }   │
└─────────────────────────────────────────────────────┘
```

---

## 🌐 API Design

### Design Principles

**1. Resource-based routing via DRF Router**

All CRUD-able models are registered with `DefaultRouter`. This auto-generates the full suite of `GET /resource/`, `POST /resource/`, `GET /resource/{id}/`, `PUT`, `PATCH`, `DELETE` endpoints with zero boilerplate.

```python
# myapp/urls.py
router = DefaultRouter()
router.register(r'users',            UserViewSet)
router.register(r'agents',           AgentViewSet)
router.register(r'conversations',    ConversationViewSet)
router.register(r'chat-messages',    ChatMessageViewSet)
router.register(r'api-keys',         APIKeyViewSet, basename="api-keys")
router.register(r'agent-feedbacks',  AgentFeedbackViewSet)
# ... more
```

**2. Action-based endpoints for complex operations**

Operations that don't map cleanly to a resource (calling an AI agent, starting a new chat, deleting a conversation) are implemented as explicit `APIView` subclasses with `path()` declarations. This keeps the router clean and the custom logic readable.

**3. Scoped querysets — users only ever see their own data**

Every `ModelViewSet` that handles user-owned data overrides `get_queryset()`:

```python
class ConversationViewSet(ModelViewSet):
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

This pattern is consistent across `ChatMessageViewSet`, `TokenLogViewSet`, `SubscriptionViewSet`, `RootAgentMemoryViewSet`, `APIKeyViewSet`, and `AgentFeedbackViewSet`. No view ever returns another user's data.

**4. Parser flexibility**

AI agent endpoints accept JSON, form data, and file uploads in one view class:

```python
class AgentAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
```

---

## 🔐 Authentication & Authorization

This project implements **two completely parallel authentication backends**, both active simultaneously via DRF's `DEFAULT_AUTHENTICATION_CLASSES`.

### Backend 1: JWT Authentication (SimpleJWT)

Standard stateless JWT flow. Users log in to receive an `access` token (30-day lifetime) and a `refresh` token (30-day lifetime). Logout blacklists the refresh token using SimpleJWT's token blacklist app, making it truly invalidate.

```python
# settings.py
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

The login view uses a custom serializer that injects extra user metadata into the JWT response without modifying the token payload itself:

```python
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'user_id':  self.user.id,
            'username': self.user.username,
            'email':    self.user.email,
        })
        return data
```

### Backend 2: API Key Authentication (Custom)

A fully custom `BaseAuthentication` subclass that supports **scoped, per-agent API keys** for external integrations. This lets third-party apps embed API access without giving out a user's full JWT.

```python
# myapp/authentication.py
class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # fall through to next auth backend

        key = auth_header.split("Bearer ")[1].strip()
        api_key = APIKey.objects.get(key=key, is_active=True)

        # Attach the key object to request for downstream ACL checks
        request.api_key = api_key
        return (api_key.user, None)
```

**Key design decisions:**
- Returns `None` (not an exception) when no `sk_*` key is detected, allowing DRF to fall through to JWT auth — both backends coexist without conflict
- Attaches the `api_key` object to the `request` so views can check granular permissions downstream without another DB query
- API keys are generated with `secrets.token_hex(16)` prefixed with `sk_` — never stored in plaintext in logs

### Per-Agent Access Control

Each `APIKey` model instance has 8 boolean permission flags — one per agent:

```
allow_qna | allow_data | allow_talent | allow_stock |
allow_resume | allow_sentiment | allow_auto | allow_rag
```

A static helper method on the auth class checks these:

```python
@staticmethod
def check_agent_permission(request, agent_name: str):
    api_key = getattr(request, "api_key", None)
    agent_map = {
        "qna":       api_key.allow_qna,
        "data":      api_key.allow_data,
        "stock":     api_key.allow_stock,
        # ...
    }
    if not agent_map.get(agent_name):
        raise AuthenticationFailed(f"API Key not authorized for {agent_name} agent.")
```

A separate `api_key_helpers.py` service module handles lookups cleanly:

```python
AGENT_FLAG_MAP = {
    "qna": "allow_qna", "data": "allow_data", ...
}

def api_key_allows_agent(api_key_obj: APIKey, agent_name: str) -> bool:
    flag = AGENT_FLAG_MAP.get(agent_name.lower())
    return bool(getattr(api_key_obj, flag, False))
```

---

## 🗃️ Data Models

All models live in `myapp/models.py`. The schema is designed around a **user → conversation → message** hierarchy with supporting lookup tables.

### Entity Relationship Overview

```
User
 ├── Conversation  (one user → many conversations)
 │    └── ChatMessage  (one conversation → many messages)
 │         └── TokenLog  (one message → one token log entry)
 ├── Subscription  (token limit / billing plan)
 ├── APIKey        (external access keys with per-agent flags)
 ├── AgentFeedback (rating + comment per agent)
 └── RootAgentMemory  (routing decisions log)

Agent
 ├── Conversation  (FK — which agent was used)
 ├── ChatMessage   (FK — which agent sent/received)
 ├── AgentIntegration  (API endpoint config for snippet gen)
 └── AgentFeedback (FK)
```

### Custom User Model

Uses `AbstractUser` with email as the login identifier. This is set up from the very first migration — changing `USERNAME_FIELD` after the fact would require a full migration rewrite.

```python
class User(AbstractUser):
    email   = models.EmailField(unique=True)
    phone   = models.CharField(max_length=12, blank=True)
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']
```

`AUTH_USER_MODEL = "myapp.User"` is set in `settings.py` before any auth-related migrations run.

### Notable Model Patterns

**Soft FK with `SET_NULL`** — conversations survive agent deletion:
```python
agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True)
```

**Auto-title on save** — conversations without a title default cleanly:
```python
def save(self, *args, **kwargs):
    if not self.title:
        self.title = "New Chat"
    super().save(*args, **kwargs)
```

**JSONField for flexible storage** — routing decisions and API request bodies stored without schema lock-in:
```python
used_agents = models.JSONField()      # on RootAgentMemory
body        = models.JSONField()      # on AgentIntegration
```

**Secure key generation on serializer create** — keys are never accepted from client input:
```python
class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ["id", "key", "user", "created_at"]

    def create(self, validated_data):
        validated_data["key"] = "sk_" + secrets.token_hex(16)
        return super().create(validated_data)
```

### Migrations

3 migrations cover the full schema evolution:

| Migration | Change |
|---|---|
| `0001_initial` | Full schema: User, Agent, Conversation, ChatMessage, TokenLog, Subscription, RootAgentMemory, APIKey, AgentFeedback |
| `0002_apikey_is_active` | Adds `is_active` flag to `APIKey` |
| `0003_alter_user_name_alter_user_phone` | Adjusts field constraints on User |

---

## ⚡ The AI Gateway Layer

`myapp/services/ai_gateway.py` is the single integration point between the Django view layer and the CrewAI agent system. This decoupling is intentional — views never import agent code directly.

```python
def call_ai_agent(agent_type: str, query, file_path=None, csv_file=None):
    if agent_type == "qna":
        from myapp.ai.agents.qna_agent.qna_user_agent import run_qna
        return run_qna(query)

    elif agent_type == "data":
        from myapp.ai.agents.data_analysis... import run_data_analysis
        return run_data_analysis(query, file_path)

    elif agent_type == "root":
        from myapp.ai import main
        return main.manager_agent_function(query=query, file=file_path)
    # ... etc
```

**Why lazy imports (inside the function, not at top of file)?**

All agent imports are deferred until the function is actually called. This means:
- Django startup time is not affected by heavy CrewAI/LangChain import chains
- A missing dependency in one agent doesn't crash the entire server
- Each agent is only loaded into memory when it's actually needed

**Why a service layer instead of calling agents directly from views?**

- Views stay clean and focused on HTTP concerns (parsing, auth, response shaping)
- Swapping an agent's implementation requires zero view changes
- The gateway is the single place to add cross-cutting concerns (logging, rate limiting, caching) for all agent calls

---

## 🧰 Custom Middleware & Response Standardization

### Standardized Response Envelope

Every single response from every endpoint is automatically wrapped in the same JSON shape via a custom DRF renderer — no decorator, no mixin, just one class registered globally:

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("myapp.utils.custom_response.CustomJSONRenderer",),
}
```

```python
# myapp/utils/custom_response.py
class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response")
        success  = response is not None and response.status_code < 400

        envelope = {
            "meta":    data if success else {},
            "message": data.pop("message", "Success") if success else str(data.get("detail", "An error occurred")),
            "error":   not success
        }
        return super().render(envelope, accepted_media_type, renderer_context)
```

**Result:** Every response, including DRF validation errors and 404s, returns:
```json
{
  "meta":    { "conversation_id": 42, "ai_reply": "..." },
  "message": "Success",
  "error":   false
}
```

### Custom Exception Handler

DRF's default exception handler is replaced with one that ensures error responses match the same envelope:

```python
# myapp/utils/custom_exception_handler.py
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "meta":    {},
            "message": str(exc),
            "error":   True
        }
    return response
```

Registered globally:
```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "myapp.utils.custom_exception_handler.custom_exception_handler",
}
```

### Code Snippet Generator Service

`myapp/services/code_snippet_generator.py` generates working integration code for any agent in 4 languages (Python, JavaScript, Java, C++) based on the `AgentIntegration` model config. This powers the `/api/integration-snippet/{agent_name}/{language}/` endpoint — useful for a developer portal or documentation site.

---

## 🔒 Security Implementation

### 1. Code Injection Prevention in Data Analysis Agent

The Data Analysis agent dynamically generates and executes Python code to analyze datasets. A **static pattern blocklist** is applied to every piece of generated code before execution:

```python
DANGEROUS_PATTERNS = [
    'import os', 'import sys', 'import subprocess', 'import socket',
    'eval(', 'exec(', '__import__', 'open(', 'file(', 'input(',
    'raw_input(', 'compile(', 'globals()', 'locals()', 'vars(',
    'getattr(', 'setattr(', 'delattr('
]
```

Code containing any of these patterns is rejected before execution.

### 2. JWT Refresh Token Blacklisting

Logout genuinely invalidates tokens — the refresh token is added to SimpleJWT's blacklist table, preventing reuse even if the token hasn't expired:

```python
class LogoutView(APIView):
    def post(self, request):
        token = RefreshToken(request.data["refresh"])
        token.blacklist()
```

### 3. User Data Isolation

No view returns data belonging to another user. Every queryset is scoped to `request.user`. There is no `is_admin` bypass path in any view — admin access goes through Django's built-in `/admin/` panel.

### 4. SMTP Credential Handling

Email sender credentials (for the Automation agent) are loaded from environment variables, never hardcoded. The `EmailConfig` dataclass abstracts SMTP server selection by domain, supporting Gmail, Outlook, Yahoo, Zoho, and iCloud out of the box.

### 5. CORS & CSRF

```python
CORS_ALLOW_ALL_ORIGINS  = True   # ← restrict to specific origins in production
CORS_ALLOW_CREDENTIALS  = True
CSRF_TRUSTED_ORIGINS    = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

`SECURE_PROXY_SSL_HEADER` is required on Render (and most PaaS platforms) because the SSL termination happens at the load balancer, not at Gunicorn.

---

## 🚀 Deployment & Production Setup

### Platform: Render

Configured via `render.yaml` for one-command deployment.

```yaml
services:
  - type: web
    name: aurelius-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn myproject.wsgi --bind 0.0.0.0:$PORT --timeout 120"
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: neon-db
          property: connectionString
```

**`--timeout 120`** on Gunicorn is critical — AI agent calls can take 30–90 seconds. The default timeout of 30 seconds would kill in-flight requests.

### Static Files: Whitenoise

Whitenoise serves compressed static files directly from Gunicorn — no S3, no separate CDN needed for this scale:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← must be second
    ...
]
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
}
```

`CompressedManifestStaticFilesStorage` adds content-hash fingerprints to filenames (e.g. `base.a3f9c2.css`) so browsers cache aggressively and bust cache on deploy.

### Database: PostgreSQL via DATABASE_URL

Settings parse the `DATABASE_URL` env var manually to support Neon's `channel_binding` requirements without depending on `dj-database-url`:

```python
url   = urlparse(DATABASE_URL)
query = parse_qs(url.query)

DATABASES = {
    "default": {
        "ENGINE":       "django.db.backends.postgresql",
        "NAME":         url.path.lstrip("/"),
        "USER":         url.username,
        "PASSWORD":     url.password,
        "HOST":         url.hostname,
        "PORT":         url.port or 5432,
        "CONN_MAX_AGE": 600,
        "OPTIONS":      {"sslmode": query.get("sslmode", ["require"])[0]},
    }
}
```

`CONN_MAX_AGE: 600` enables persistent database connections — each Gunicorn worker reuses its DB connection for up to 10 minutes instead of reconnecting on every request.

### Python Version

Pinned in `runtime.txt`:
```
python-3.12.7
```

---

## 🛠️ Local Development Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/aurelius-backend.git
cd aurelius-backend

# 2. Virtual environment
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env
# Edit .env — at minimum set DATABASE_URL and GOOGLE_API_KEY

# 5. Database
python manage.py migrate

# 6. (Optional) Create superuser for /admin/
python manage.py createsuperuser

# 7. Run
python manage.py runserver
```

**Minimum required `.env` for local development:**
```env
DEBUG=True
SECRET_KEY=any-local-secret-key
DATABASE_URL=postgres://postgres:password@localhost:5432/aurelius_dev
GOOGLE_API_KEY=your-key     # required for any agent call
TAVILY_API_KEY=your-key     # required for QnA agent
```

---

## 🤝 Collaboration Guide

This section is for contributors and teammates.

### Branch Strategy

```
main          ← production-ready, deployed to Render on merge
dev           ← integration branch, all PRs target this
feature/*     ← individual feature branches (e.g. feature/stock-agent-cache)
fix/*         ← bug fix branches
```

### Adding a New Agent

The system is designed to make adding agents straightforward without touching existing code:

**Step 1** — Build the CrewAI crew under `myapp/ai/agents/your_agent/`:
```
your_agent/
  ├── crew.py              ← @CrewBase class with @agent, @task, @crew
  ├── your_agent_main.py   ← plain callable function for gateway
  ├── your_agent_root.py   ← @tool version for root orchestrator
  └── config/
       ├── agents.yaml
       └── tasks.yaml
```

**Step 2** — Register in the gateway (`myapp/services/ai_gateway.py`):
```python
elif agent_type == "your_agent":
    from myapp.ai.agents.your_agent.your_agent_main import run_your_agent
    return run_your_agent(query, file_path)
```

**Step 3** — Add permission flag to the `APIKey` model (`myapp/models.py`):
```python
allow_your_agent = models.BooleanField(default=False)
```

**Step 4** — Register in `api_key_helpers.py`:
```python
AGENT_FLAG_MAP = {
    ...
    "your_agent": "allow_your_agent",
}
```

**Step 5** — Run `python manage.py makemigrations && python manage.py migrate`

**Step 6** — Add the root orchestrator tool import in `myapp/ai/main.py`

That's it. No view changes needed.

### Code Style Conventions

- Views contain **only HTTP logic** — parsing, auth checks, calling the service layer, returning a response
- Business logic lives in `myapp/services/` or inside the agent modules
- All querysets in ViewSets are filtered to `request.user` — never return unscoped data
- Use lazy imports inside `call_ai_agent()` for all new agent integrations
- Model `__str__` methods always return something meaningful (used in admin)

### Running Tests

```bash
python manage.py test myapp
```

Test coverage targets (for contributors):
- All auth flows (signup, login, logout, token refresh)
- Queryset scoping (user A cannot read user B's conversations)
- API key permission enforcement
- Gateway routing (each agent_type routes correctly)

---

## 📡 API Reference

Base URL: `https://aurelius-backend.onrender.com` (or `http://localhost:8000` locally)

All authenticated endpoints require:
```
Authorization: Bearer <jwt_access_token_or_api_key>
```

All responses follow the envelope:
```json
{ "meta": {}, "message": "string", "error": false }
```

### Auth Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/signup/` | None | Register new user |
| `POST` | `/api/login/` | None | Login, returns JWT pair |
| `POST` | `/api/logout/` | JWT | Blacklists refresh token |
| `POST` | `/api/token/refresh/` | None | Exchange refresh → new access token |

### Agent Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/root-agent/` | JWT/Key | Auto-route query to best agent |
| `POST` | `/api/agent/{name}/` | JWT/Key | Call specific agent directly |

**Agent names:** `qna` · `data` · `auto` · `stock` · `resume` · `sentiment` · `talent` · `rag`

### Conversation Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/conversation-history/` | JWT | List all user conversations |
| `GET` | `/api/conversation/{id}/messages/` | JWT | All messages in a conversation |
| `POST` | `/api/new-chat/` | JWT | Start a fresh conversation |
| `DELETE` | `/api/conversation/{id}/delete/` | JWT | Delete conversation + messages |
| `POST` | `/api/save-chat/` | JWT | Manually save a message |

### API Key Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/api-keys/` | JWT | List user's API keys |
| `POST` | `/api/api-keys/` | JWT | Generate new scoped API key |
| `PATCH` | `/api/api-keys/{id}/` | JWT | Update key permissions |
| `DELETE` | `/api/api-keys/{id}/` | JWT | Revoke a key |

### Public Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/public-agents/` | None | List featured agents |
| `GET` | `/api/public-agents/{id}/` | None | Single agent detail |
| `GET` | `/api/integration-snippet/{agent}/{lang}/` | JWT | Get code snippet (python/javascript/java/c++) |

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `DEBUG` | ✅ | `True` for dev, `False` for prod |
| `ALLOWED_HOSTS` | ✅ | Comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | ✅ | Comma-separated trusted origins |
| `GOOGLE_API_KEY` | ✅ | Gemini LLM access (all agents) |
| `TAVILY_API_KEY` | ✅ | Web search (QnA agent) |
| `GITHUB_TOKEN` | ⚠️ | GitHub API (Talent agent only) |
| `ALPHA_VANTAGE_API_KEY` | ⚠️ | Stock data (Stock agent only) |
| `GEMINI_API_KEY` | ⚠️ | Alias for GOOGLE_API_KEY in some agents |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with Django · DRF · CrewAI · PostgreSQL · Deployed on Render
</div>
