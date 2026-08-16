# Taskello — Backend

A REST API for **Taskello**, a Trello-like task management application. Users create dashboards (boards), organize tasks into categories (columns), and collaborate through comments and file attachments.

The backend is built with **Django REST Framework** and shipped as a full Docker stack (app + PostgreSQL). Companion frontend: **[task-managment-front](https://github.com/Tchobo/task-managment-front)** (Vue 3 + Vite + Vuetify + Tailwind).

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9 |
| Framework | Django 3.2 (LTS) + Django REST Framework 3.12 |
| Database | PostgreSQL 13 |
| Auth | **Djoser** + **JWT** (`djangorestframework-simplejwt`) |
| API Doc | drf-spectacular (OpenAPI 3 + Swagger UI) |
| CORS | `django-cors-headers` (configured for the Vue frontend at `:5173`) |
| Image handling | Pillow |
| Containerization | Docker + Docker Compose |
| App server | Django dev server (production hardening on the roadmap) |

---

## Features

- **Custom User model** with email as the primary identifier
- **JWT authentication** — register, login, refresh, profile management (powered by Djoser)
- **Dashboards** — create boards for each project, each with default task categories on creation
- **Task categories (columns)** — auto-generated defaults (e.g. *To Do / In Progress / Done*), user can add / rename / reorder
- **Tasks** — full CRUD with title, description, tags, badge colors, deadline, position (fractional indexing for reordering), and file uploads
- **Comments** on tasks
- **File attachments** on tasks (multi-file upload, served via Django media handling)
- **Interactive API documentation** — Swagger UI at `/api/docs/`
- **Persistent database volume** (`pgdata`) so your data survives container restarts

---

## API endpoints

Once running, the interactive Swagger UI is available at:

```
http://localhost:8080/api/docs/
```

Main endpoint groups:

| Prefix | Purpose |
|---|---|
| `/api/user/` | Djoser + JWT auth (register, login, token refresh, profile) |
| `/api/dashboard/` | Dashboards + task categories (columns) |
| `/api/tasks/` | Tasks, comments, file attachments |
| `/api/schema/` | Raw OpenAPI 3 schema (JSON) |
| `/api/docs/` | Swagger UI |
| `/admin/` | Django admin panel |

---

## Quick start — development

### Prerequisites

- Docker + Docker Compose
- A Gmail account with an **App Password** (for outgoing email — password reset, activation, etc.)

### Setup

```bash
# 1. Clone
git clone git@github.com:Tchobo/task-management-app.git
cd task-management-app

# 2. Create your .env from the template
cp .env.example .env
# Edit .env and fill in:
#   SECRET_KEY=... (any random string for dev)
#   EMAIL_HOST_USER=your.email@gmail.com
#   EMAIL_HOST_PASSWORD=your_gmail_app_password

# 3. Build & start
docker-compose up --build

# 4. In another terminal, create a superuser (optional, for /admin/)
docker-compose run --rm app sh -c "python manage.py createsuperuser"
```

The API is now available at `http://localhost:8080/`.
Swagger UI: `http://localhost:8080/api/docs/`

> Migrations are applied **automatically** on container startup — no manual `migrate` needed.

---

## Environment variables

All configurable settings live in the `.env` file at the repository root.
The `.env.example` file is committed as a template — copy it to `.env` and fill in your values.

| Variable | Purpose | Committed |
|---|---|:---:|
| `SECRET_KEY` | Django secret key | ❌ |
| `EMAIL_HOST_USER` | Gmail address used to send outgoing mail | ❌ |
| `EMAIL_HOST_PASSWORD` | [Gmail App Password](https://support.google.com/mail/answer/185833) (not your account password) | ❌ |
| `DEBUG` | `1` for local dev, `0` for production | ✅ (in `docker-compose.yml`) |
| `DB_*` | Postgres connection details for dev | ✅ (in `docker-compose.yml`) |
| `CORS_ALLOWED_ORIGINS` | Origins allowed by CORS (default: Vue dev at `:5173`) | ✅ (in `docker-compose.yml`) |
| `ALLOWED_HOSTS` | Django ALLOWED_HOSTS setting | ✅ (in `docker-compose.yml`) |

---

## Companion frontend

The Vue 3 frontend for this API lives in a separate repository:
👉 **[task-managment-front](https://github.com/Tchobo/task-managment-front)**

The frontend expects the backend to be running at `http://localhost:8080` and itself runs on `http://localhost:5173` (Vite default). CORS is already configured to allow this origin.

---

## Project structure

```
task-management-app/
├── app/                              # Django project root
│   ├── app/                          # Project settings, main URLconf, WSGI/ASGI
│   ├── core/                         # Custom User, Dashboard, TaskCategorie, Task, TaskComment, MediaFile
│   ├── account/                      # Registration, login (Djoser + JWT), profile
│   ├── dashboard/                    # Dashboard + TaskCategorie CRUD
│   ├── tasks/                        # Task CRUD, comments, file uploads
│   ├── templates/                    # Email templates (activation, password reset)
│   └── manage.py
├── data/web/                         # Docker volume mount point for uploaded media
├── Dockerfile                        # Alpine-based image (Python 3.9)
├── docker-compose.yml                # Dev stack (app + Postgres, with pgdata volume)
├── requirements.txt                  # Runtime dependencies
├── .env.example                      # Template for local environment variables
└── .gitignore
```

---

## Development notes

### Active branches

- **`main`** — clean, deployable state
- **`feat/assign-to`** — work-in-progress: assigning a task to a specific user (`assign_To` field on Task model). Not merged pending design decisions (ForeignKey vs ManyToMany) and test cleanup.

---

## Roadmap — planned enhancements

- [ ] **Complete `feat/assign-to`** — resolve FK vs M2M design, fix duplicate test names, merge to main
- [ ] Upgrade to **Django 5.x** + **DRF 3.15+** + Python 3.12
- [ ] Migrate from `flake8` (implicit) to **ruff** (linter + formatter) with CI enforcement
- [ ] Add **mypy** static type checking
- [ ] Add **pytest** + coverage reporting (`--cov-fail-under=80`)
- [ ] Add **rate limiting** (DRF throttling)
- [ ] Add **pagination** on tasks and dashboards list endpoints
- [ ] Add a **health check** endpoint (`/health/`) for monitoring
- [ ] Switch from Django dev server to **uWSGI / Gunicorn + nginx** for production
- [ ] Add **GitHub Actions CI** (test + lint on every push)
- [ ] Publish container images to a public registry (GHCR)

---

## License

MIT — provided as-is for portfolio and learning purposes.

---

## Author

**Toussaint Tchodo** — Backend engineer specializing in Django, SaaS multi-tenant architectures, and API security.
[GitHub](https://github.com/Tchobo) · [LinkedIn](https://www.linkedin.com/in/toussaint-tchodo/)
