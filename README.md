# BunCNAME

A tool to synchronize DNS records across multiple DNS providers.

## Supported Providers

- Cloudflare
- Porkbun
- AdGuard Home

## Configuration

Create a `.env` file with your credentials:

```env
# Cloudflare
CLOUDFLARE_API_TOKEN=your_api_token

# Porkbun
PORKBUN_API_KEY=your_api_key
PORKBUN_SECRET_KEY=your_secret_key

# AdGuard Home
ADGUARD_HOME_URL=http://your-adguard-home:8080
ADGUARD_HOME_USERNAME=admin
ADGUARD_HOME_PASSWORD=password

# Optional
PORT=8000
SYNC_TOKEN=shared_secret_for_the_sync_endpoint
MANAGED_TYPES=CNAME
```

Cloudflare notes: the token needs `Zone - Read` + `DNS - Edit` (scope it to
your zone if possible). Records are created as DNS-only (`proxied=false`) and
TTL is clamped to the Cloudflare minimum of 60.

### Optional settings

- `SYNC_TOKEN` — when set, `POST /sync` requires an `X-Sync-Token` request
  header with the same value (compared in constant time). Strongly
  recommended whenever the service is reachable by anything you don't fully
  trust, because `/sync` reconciles destructively: managed records that are
  absent from the payload get **deleted**.
- `MANAGED_TYPES` — comma-separated whitelist of record types the reconciler
  touches (default `CNAME`). Anything else on the provider is left alone.
  Set `CNAME,A` to also manage A records.

### Sync responses

`/sync` returns a per-domain summary (`created` / `updated` / `deleted` /
`errors` per domain and provider). If any provider action fails the endpoint
answers HTTP 500 with the summary instead of silently pretending success.

## Records Configuration

The HTTP payload format is the same as the previous `records.json` schema:

```json
[
  {
    "domain": "example.com",
    "providers": ["porkbun", "adguard_home"],
    "records": [
      {
        "host": "www",
        "type": "CNAME",
        "content": "target.io",
        "ttl": 600
      }
    ]
  }
]
```

`providers` can be a string or an array of strings for multiple providers.

## Notes

- For AdGuard Home, rewrite rules are managed for both domain answers (mapped
  to CNAME) and IP answers (mapped to A/AAAA). Enable `A` in `MANAGED_TYPES`
  to manage the latter.
- The tool will create, update, or delete records to match the desired state in the payload you send.

## PocketBase auto-sync (optional)

`pb_hooks/dns_sync.pb.js` turns PocketBase into the desired-state source: any
create/update/delete on the `domains` or `dns_records` collections rebuilds
the full payload from the database and pushes it to `/sync`; a cron job
re-pushes every 5 minutes as a drift safety net.

Collections expected by the hook:

- `domains`: `domain` (text), `providers` (text — JSON array or comma list)
- `dns_records`: `domain` (relation → `domains`), `host`, `type`, `content`, `ttl` (number)

Run PocketBase with the hook and point it at the sync service:

```bash
BUNSYNC_URL=http://127.0.0.1:8000/sync BUNSYNC_TOKEN=your_sync_token \
  ./pocketbase serve --dir=/srv/buncname/pb_data --hooksDir=/srv/buncname/pb_hooks
```

Gotchas verified against PocketBase v0.23.9:

- Hook callbacks run in pooled JS runtimes: closures and top-level
  declarations from the hook file are **not** visible inside a callback, and
  an exception thrown in a callback turns an already-persisted record write
  into a failed (400) request. That is why every callback in the hook is
  fully self-contained — don't extract shared helpers without re-testing.
- `pb_data` is resolved relative to the **binary's directory**, not the
  working directory. Always pass `--dir` explicitly (to `serve` *and*
  `superuser upsert`), otherwise they operate on different databases.
- If a collection has no `created` field, don't use `-created` as the sort in
  `findRecordsByFilter`.
- Until both collections exist, the cron job logs a harmless
  `sql: no rows in result set` error every 5 minutes.

## Docker Compose

A `docker-compose.yml` is included that wires up the sync service together
with PocketBase and AdGuard Home. Copy `.env.example` to `.env`, fill in
credentials, then `docker compose up -d`.

## Running as HTTP service

Start the app:

```bash
pip install -r requirements.txt
python main.py
```

Then push the JSON payload to:

```bash
curl -X POST http://localhost:8000/sync \
  -H "Content-Type: application/json" \
  -d '[
    {
      "domain": "example.com",
      "providers": ["porkbun"],
      "records": [
        {"host": "www", "type": "CNAME", "content": "target.io", "ttl": 600}
      ]
    }
  ]'
```

Response:

```json
{"status": "ok", "message": "DNS sync completed", "records": 1}
```

## SQL Schemas

There is an `sql/` folder included with two reference SQL files that show example table schemas you can use if you want to store desired records in a database and drive syncs from that data:

- `sql/domains.sql` — reference table for domains and metadata (e.g. domain name, provider list).
- `sql/dns_records.sql` — reference table for DNS records associated with domains (e.g. host, type, content, ttl).

These files are intended as examples only; adjust column types/names to match your database conventions.

## Using your own database with BunCNAME

1. Create the tables in your database using the SQL files in `sql/` (for example, via `psql` or `mysql` depending on your DB):

```bash
# Example for PostgreSQL
psql -U <user> -d <db> -f sql/domains.sql
psql -U <user> -d <db> -f sql/dns_records.sql
```

2. Populate the tables with the desired domain/record rows.

3. Query your database to produce a JSON payload that matches the `records.json` schema used by this project (an array of domain objects, each with `domain`, `providers`, and `records`).

4. POST that JSON to the running BunCNAME service to trigger a sync:

```bash
curl -X POST http://localhost:8000/sync \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Where `payload.json` contains the exported JSON from your DB, e.g.:

```json
[
  {
    "domain": "example.com",
    "providers": ["porkbun"],
    "records": [
      {"host": "www", "type": "CNAME", "content": "target.io", "ttl": 600}
    ]
  }
]
```

This approach keeps the sync logic in BunCNAME (the HTTP endpoint) while letting you manage desired state in whatever database you prefer.