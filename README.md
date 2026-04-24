# Petso API

Django REST API for Petso (users, farmers, vets, companies, ecommerce, orders, payments, medical, social, chat, AI).

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env   # then edit secrets
python manage.py migrate
python manage.py runserver
```

- API docs: `http://127.0.0.1:8000/api/docs/`
- Postman: import `Petso_Postman_Collection.json` (local + OTP) or `Petso_Postman_Collection.Production.json` (Vercel, no OTP). Regenerate: `python tools/build_postman_collection.py`.

## GitHub

```bash
git remote add origin https://github.com/kamelfcis/Petso-API.git
git push -u origin main
```

## Vercel

Repository: [github.com/kamelfcis/Petso-API](https://github.com/kamelfcis/Petso-API).

This project was linked for deployment; production URL (after env is configured): **https://petso-api.vercel.app**

1. In the Vercel project **Settings → Environment Variables**, set at least:

| Variable | Example |
|----------|---------|
| `SECRET_KEY` | long random string |
| `DEBUG` | `False` |
| `DATABASE_URL` | **Leave unset** to use bundled `deployment/petso.sqlite3` (copied to `/tmp` on Vercel). Set to `postgres://...` for persistent production data. |
| `ALLOWED_HOSTS` | `.vercel.app,your-project.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app` |
| `REDIS_URL` | managed Redis URL (Upstash etc.); if unset on Vercel, Channels uses an in-memory layer (HTTP works; WS limited) |
| `CELERY_BROKER_URL` | same or separate Redis DB index |

2. **Postgres strongly recommended:** set `DATABASE_URL` in Vercel, then run `python manage.py migrate` against that database (e.g. `vercel env pull` locally, then migrate). Without it, the app may use ephemeral SQLite under `/tmp` and still error until migrations exist on a persistent DB.

3. Vercel sets `VERCEL=1` automatically; the project uses that for safer defaults (writable SQLite path, in-memory Channels when no `REDIS_URL`).

**Same database for `/admin/` and `/api/`:** Django uses a single `DATABASES['default']`. With the bundled SQLite (leave `DATABASE_URL` unset), JWT login and the admin panel both use that same DB. Bundled demo admin: `admin@petso.local` / `PetsoVercel2026!` (see `deployment/README.md`). If you use Postgres instead, point `DATABASE_URL` at one database and run `migrate` + create a superuser there—both admin and API use that URL.

**Limits:** Celery workers and long-lived WebSockets are not first-class on Vercel serverless. Email OTP and background tasks need an external worker (e.g. Railway, Render, or a VPS) calling the same Redis/DB, or refactors to synchronous/email providers.

## Admin dashboard in production

**URL:** `https://<your-domain>/admin/` — e.g. `https://petso-api.vercel.app/admin/`

### 1. Database and migrations

Use a **persistent Postgres** `DATABASE_URL` on Vercel (not ephemeral `/tmp` SQLite). Then apply migrations **to that same database** from your machine:

```bash
vercel env pull .env.vercel
# Edit .env.vercel if needed so DATABASE_URL points at production Postgres
set DJANGO_SETTINGS_MODULE=petso_project.settings
python manage.py migrate
```

(On macOS/Linux use `export` instead of `set`.)

### 2. Create a superuser (pick one way)

**A — Interactive (local shell, same `DATABASE_URL` as production):**

```bash
python manage.py createsuperuser
```

Enter **email** (this project uses email as login), **name**, and **password**.

**B — Non-interactive (Django built-in, same env as production):**

```bash
set DJANGO_SUPERUSER_EMAIL=you@example.com
set DJANGO_SUPERUSER_PASSWORD=your-strong-password
set DJANGO_SUPERUSER_NAME=Your Name
python manage.py createsuperuser --noinput
```

**C — Project helper (reads `BOOTSTRAP_*` env vars, skips if user exists):**

```bash
set BOOTSTRAP_ADMIN_EMAIL=you@example.com
set BOOTSTRAP_ADMIN_PASSWORD=your-strong-password
set BOOTSTRAP_ADMIN_NAME=Admin
python manage.py bootstrap_admin
```

Remove bootstrap password from your shell history after use; do not commit these values.

### 3. Vercel environment variables for login / CSRF

Set in the Vercel dashboard (Production):

| Variable | Purpose |
|----------|---------|
| `DEBUG` | `False` for real production |
| `ALLOWED_HOSTS` | `petso-api.vercel.app,.vercel.app` (include your exact host) |
| `CSRF_TRUSTED_ORIGINS` | `https://petso-api.vercel.app` (must match how you open the site in the browser) |

After changing env vars, trigger a **Redeploy** so the app picks them up.

### 4. Sign in

Open `/admin/`, log in with the **superuser email** and **password** you created (not the Jazzmin “username” field if it appears — this project’s `USERNAME_FIELD` is **email**).
