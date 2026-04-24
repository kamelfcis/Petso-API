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

1. Push this repo to GitHub, then in [Vercel](https://vercel.com) **Add New Project** → import `kamelfcis/Petso-API`.
2. Set **Environment variables** (minimum for a working deploy):

| Variable | Example |
|----------|---------|
| `SECRET_KEY` | long random string |
| `DEBUG` | `False` |
| `DATABASE_URL` | Postgres URL (e.g. Neon/Vercel Postgres); avoid SQLite on Vercel |
| `ALLOWED_HOSTS` | `.vercel.app,your-project.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app` |
| `REDIS_URL` | managed Redis URL (Upstash etc.) |
| `CELERY_BROKER_URL` | same or separate Redis DB index |

3. After first deploy, run migrations against the production database (Vercel **CLI** `vercel env pull` + local `manage.py migrate`, or a one-off script).

**Limits:** Celery workers and long-lived WebSockets are not first-class on Vercel serverless. Email OTP and background tasks need an external worker (e.g. Railway, Render, or a VPS) calling the same Redis/DB, or refactors to synchronous/email providers.
