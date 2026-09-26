# THE SYSTEM — Cloudflare deployment

This package converts the Python/SQLite local version to a Cloudflare Worker + D1 deployment while preserving the existing frontend API contract.

## 1. Create D1
Cloudflare Dashboard → Workers & Pages → D1 SQL database → Create database.
Name it `the-system-db`.

## 2. Run schema
Use D1 Console / SQL editor and paste the contents of `migrations/0001_initial.sql`.

## 3. Connect repository
Use GitHub integration. The project root must contain `worker.js`, `wrangler.toml`, `migrations/`, and `public/`.

## 4. Configure build
No build command is required. Deployment uses Wrangler. If the dashboard asks for a deploy command, use:
`npx wrangler deploy`

The asset directory is `public/`, and the Worker is `worker.js`.

## 5. Set secret
Create a Worker secret named `TOKEN_SECRET` with a long random value. Do not commit it to GitHub.

## 6. D1 binding
In `wrangler.toml`, replace `REPLACE_WITH_YOUR_D1_DATABASE_ID` with the database ID shown by Cloudflare.

## 7. Important
Do not upload `system.sqlite3`, `*.sqlite3-shm`, or `*.sqlite3-wal` to GitHub. They are local database files and are not used by this cloud build.
