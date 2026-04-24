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
- Postman: import `Petso_Postman_Collection.json` (regenerate with `python tools/build_postman_collection.py`).

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
| `DATABASE_URL` | Postgres URL (e.g. Neon/Vercel Postgres); avoid SQLite on Vercel |
| `ALLOWED_HOSTS` | `.vercel.app,your-project.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app` |
| `REDIS_URL` | managed Redis URL (Upstash etc.); if unset on Vercel, Channels uses an in-memory layer (HTTP works; WS limited) |
| `CELERY_BROKER_URL` | same or separate Redis DB index |

2. **Postgres strongly recommended:** set `DATABASE_URL` in Vercel, then run `python manage.py migrate` against that database (e.g. `vercel env pull` locally, then migrate). Without it, the app may use ephemeral SQLite under `/tmp` and still error until migrations exist on a persistent DB.

3. Vercel sets `VERCEL=1` automatically; the project uses that for safer defaults (writable SQLite path, in-memory Channels when no `REDIS_URL`).

**Limits:** Celery workers and long-lived WebSockets are not first-class on Vercel serverless. Email OTP and background tasks need an external worker (e.g. Railway, Render, or a VPS) calling the same Redis/DB, or refactors to synchronous/email providers.
