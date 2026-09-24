# EduConnect — Cloudflare Deployment

This project is prepared for a free Cloudflare deployment using:

- React + Vite frontend on Cloudflare Pages
- Django REST API on Cloudflare Workers (Python Workers)
- Cloudflare D1 for the production SQLite-compatible database

## 1. Create the D1 database

From the `backend` directory:

```bash
npx wrangler d1 create educonnect-db
```

Copy the returned database ID into `backend/wrangler.jsonc`:

```jsonc
"database_id": "YOUR_REAL_D1_DATABASE_ID"
```

Do not commit API tokens or other Cloudflare credentials.

## 2. Install the Python Worker tooling

Install `uv` and Node.js, then from `backend` run:

```bash
uv run pywrangler dev
```

Cloudflare's Python Workers tooling bundles the dependencies from `pyproject.toml` when the Worker is deployed.

## 3. Create the production schema

D1 uses SQL migration files. Do not run Django's test suite against the production D1 database. Keep local Django tests on SQLite or use a separate test database.

Before the first production deployment, generate/verify the SQL schema from the current Django migrations and place the resulting SQL files under `backend/cloudflare_migrations/`.

Apply them with:

```bash
npx wrangler d1 migrations apply educonnect-db --remote
```

## 4. Configure Worker secrets

Set these with Wrangler rather than committing them:

```bash
npx wrangler secret put DJANGO_SECRET_KEY
npx wrangler secret put GROK_API_KEY
```

Optional secrets for email and OAuth can be added later if those features are enabled in production.

## 5. Deploy the Django API

From `backend`:

```bash
uv run pywrangler deploy
```

Cloudflare will provide a `workers.dev` URL.

## 6. Configure the frontend

Set the Vite production variable to the Worker URL without `/api`:

```env
VITE_BACKEND_URL=https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev
```

The existing Axios configuration appends `/api` to this base URL.

## 7. Deploy the React frontend

In Cloudflare Dashboard:

1. Workers & Pages → Create application → Pages → Connect to Git.
2. Select `Beebek-Sharma/EduConnect`.
3. Set the root directory to `frontend`.
4. Build command: `npm run build`.
5. Build output directory: `dist`.
6. Add `VITE_BACKEND_URL` as a production environment variable.
7. Deploy.

Cloudflare will automatically redeploy the frontend when changes are pushed to the selected Git branch.

## Important production notes

- Keep `.env`, `.env.*` and database files out of Git.
- Never put `DJANGO_SECRET_KEY`, `GROK_API_KEY`, OAuth secrets, or email passwords in Vite variables because Vite variables are exposed to the browser.
- Use a separate D1 database for testing/staging. Do not run `python manage.py test` against production D1.
- D1 does not provide normal database transactions, so application code relying on rollback/atomic transaction semantics must be reviewed before production use.
- D1/Django compatibility should be tested for the admin interface and any SQLite-specific ORM operations before calling the deployment production-ready.
