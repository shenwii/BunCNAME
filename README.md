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
CONFIG_PATH=records.json
SYNC_INTERVAL=30  # minutes
```

## Records Configuration

Edit `records.json` to define the records to sync:

```json
[
  {
    "domain": "example.com",
    "provider": ["porkbun", "adguard_home"],
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

`provider` can be a string or an array of strings for multiple providers.

## Notes

- For AdGuard Home, only CNAME-like rewrite rules are managed (domain to domain mappings). A records (domain to IP) are ignored.
- The tool will create, update, or delete records to match the desired state in `records.json`.

## Running

```bash
python main.py
```