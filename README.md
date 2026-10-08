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