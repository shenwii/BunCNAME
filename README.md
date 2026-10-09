# BunCNAME

A tool to synchronize DNS records across multiple DNS providers.

## Supported Providers

- Porkbun
- AdGuard Home

## Configuration

Create a `.env` file with your credentials:

```env
# Porkbun
PORKBUN_API_KEY=your_api_key
PORKBUN_SECRET_KEY=your_secret_key

# AdGuard Home
ADGUARD_HOME_URL=http://your-adguard-home:8080
ADGUARD_HOME_USERNAME=admin
ADGUARD_HOME_PASSWORD=password

# Optional
PORT=8000
```

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

- For AdGuard Home, only CNAME-like rewrite rules are managed (domain to domain mappings). A records (domain to IP) are ignored.
- The tool will create, update, or delete records to match the desired state in the payload you send.

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