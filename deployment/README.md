# Bundled SQLite for Vercel

This folder contains **`petso.sqlite3`**: a migrated database copied into `/tmp` on each Vercel cold start (see `petso_project/settings.py`).

## Default admin (change after first login)

| Field    | Value               |
|----------|---------------------|
| Email    | `admin@petso.local` |
| Password | `PetsoVercel2026!`  |

## Rebuild the file locally

```bash
python manage.py build_vercel_sqlite
# optional: --email you@example.com --password YourSecurePass
```

Then commit `deployment/petso.sqlite3` and push. On Vercel, **remove** `DATABASE_URL` (or leave unset) so the bundled copy is used—not a `sqlite:` URL under `/var/task`.

**Note:** Data written on Vercel (e.g. new users) lives only until the next cold start, when the DB is recopied from the bundle.
