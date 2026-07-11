# Hikaya

Restaurant menu and admin backend built with FastAPI, MySQL, JWT authentication, Alembic migrations, and a Jinja2 HTML frontend on a Bootstrap 5 admin template.

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Web framework | FastAPI |
| Server | Uvicorn |
| ORM | SQLAlchemy 2.x |
| Database | MySQL (via PyMySQL) |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt |
| Config | pydantic-settings + python-dotenv |
| Templating | Jinja2 |
| Frontend | Bootstrap 5 (admin template) |

---

## Project Structure

```
project/
├── app/                        # Python application code
│   ├── main.py                 # FastAPI app entry point, static mounts
│   ├── core/
│   │   ├── config.py           # Settings from .env (pydantic-settings)
│   │   ├── database.py         # SQLAlchemy engine, session, Base
│   │   ├── deps.py             # Cookie/Bearer auth dependencies
│   │   └── security.py         # bcrypt hashing + JWT encode/decode
│   ├── models/
│   │   └── user.py             # User model (id, email, hashed_password, is_active, timestamps)
│   ├── schemas/
│   │   └── auth.py             # Pydantic schemas: LoginRequest, TokenResponse, UserOut
│   └── api/v1/
│       ├── router.py           # API v1 router
│       └── endpoints/
│           ├── health.py       # GET /api/v1/health, GET /api/v1/db-check
│           ├── auth.py         # POST /api/v1/auth/login, GET /api/v1/auth/me
│           └── web.py          # HTML admin routes (/admin/login, /admin/dashboard, /admin/logout)
│
├── views/                      # Jinja2 HTML templates
│   ├── base.html               # Base layout (shared scripts, auth guard, logout)
│   ├── login.html              # Login page (standalone, no sidebar)
│   ├── dashboard.html          # Dashboard page (extends base.html)
│   └── components/
│       ├── header.html         # Top navbar component ({% include %})
│       └── sidebar.html        # Sidebar navigation component ({% include %})
│
├── template/                   # Vendor Bootstrap 5 admin template (source assets)
│   ├── assets/                 # Served at /assets
│   └── sass/                   # Served at /sass
│
├── alembic/                    # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── scripts/
│   └── create_admin.py         # Seed an admin user from env vars
│
├── .env                        # Secret config (gitignored)
├── .env.example                # Config template (safe to commit)
├── .gitignore
├── alembic.ini
├── requirements.txt
└── run.py                      # Shortcut: python run.py
```

---

## Quick Start

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd <project>
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=youruser
DB_PASSWORD=yourpassword
DB_NAME=yourdb

SECRET_KEY=<run: openssl rand -hex 32>
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

> The `DATABASE_URL` is built automatically from the individual vars — no need to set it manually. Special characters in the password are URL-encoded automatically.

### 4. Run migrations

```bash
# Apply existing migrations
alembic upgrade head

# After changing models, generate a new migration
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

### 5. Create first user

```bash
ADMIN_EMAIL=you@example.com ADMIN_PASSWORD=yourpassword python scripts/create_admin.py
```

### 6. Run the server

```bash
python run.py
```

Or with Uvicorn directly:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## Pages

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/` | Redirects to `/admin/login` |
| `http://127.0.0.1:8000/admin/login` | Login page |
| `http://127.0.0.1:8000/admin/dashboard` | Dashboard (server-side cookie auth required) |
| `http://127.0.0.1:8000/admin/logout` | Clears auth cookie and redirects to login |
| `http://127.0.0.1:8000/docs` | Swagger UI (API docs) |

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/health` | No | Server health check |
| GET | `/api/v1/db-check` | No | Database connectivity check |
| POST | `/api/v1/auth/login` | No | Login → returns JWT |
| GET | `/api/v1/auth/me` | Bearer | Returns current user info |

### Login example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'
```

---

## Adding a New Page

1. Create `views/your-page.html`:

```html
{% extends "base.html" %}

{% block title %}Project — Your Page{% endblock %}

{% block content %}
  <!-- your content here -->
{% endblock %}

{% block extra_js %}
<script>
  // page-specific JS
</script>
{% endblock %}
```

2. Add a route in `app/api/v1/endpoints/web.py`:

```python
@router.get("/admin/your-page", response_class=HTMLResponse, include_in_schema=False)
def your_page(request: Request, user: User = Depends(require_html_user)):
    return templates.TemplateResponse("your-page.html", {"request": request, "user": user})
```

3. Add it to the sidebar in `views/components/sidebar.html`.

---

## Adding a New API Route

1. Create `app/api/v1/endpoints/your_resource.py`
2. Define your router and endpoints
3. Import and include it in `app/api/v1/router.py`

---

## Template System

| File | Role |
|---|---|
| `views/base.html` | Shared layout: CSS, JS, user display, sidebar/header includes |
| `views/components/header.html` | Top navbar — included via `{% include %}` in base |
| `views/components/sidebar.html` | Sidebar nav — included via `{% include %}` in base |
| `views/login.html` | Standalone (does not extend base — different layout) |

Protected admin pages use server-side cookie authentication via `require_html_user` in `app/core/deps.py`. Unauthenticated requests receive an HTTP redirect to `/admin/login`.

---

## Notes

- Passwords are hashed with **bcrypt** — never stored in plain text
- HTML admin auth uses an **httpOnly cookie** (`access_token`); API clients can still use Bearer tokens
- Set `COOKIE_SECURE=true` in production so the auth cookie is only sent over HTTPS
- `DATABASE_URL` uses `urllib.parse.quote_plus` to handle special characters in passwords
- Alembic's `env.py` escapes `%` characters in the URL to avoid ConfigParser interpolation errors
- `main.js` from the vendor template requires `.search-content` and `.notify-list` elements — a hidden stub div is included in `base.html` to prevent crashes
