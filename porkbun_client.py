from typing import List, Dict, Any
from dns_provider import DNSProvider
import requests

class PorkbunClient(DNSProvider):
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        

    def get_records(self, domain: str) -> List[Dict[str, Any]]:
        """Retrieve all DNS records for a domain."""
        url = f"https://api.porkbun.com/api/json/v3/dns/retrieve/{domain}"
        data = {
            "apikey": self.api_key,
            "secretapikey": self.secret_key
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get("records", [])

    def create_record(self, domain: str, host: str, rtype: str, content: str, ttl: int = 600):
        """Create a new DNS record."""
        url = f"https://api.porkbun.com/api/json/v3/dns/create/{domain}"
        data = {
            "apikey": self.api_key,
            "secretapikey": self.secret_key,
            "name": host,
            "type": rtype,
            "content": content,
            "ttl": ttl
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def delete_record(self, domain: str, record_id: str):
        """Delete a DNS record by ID."""
        url = f"https://api.porkbun.com/api/json/v3/dns/delete/{domain}/{record_id}"
        data = {
            "apikey": self.api_key,
            "secretapikey": self.secret_key
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def edit_record(self, domain: str, record_id: str, host: str, rtype: str, content: str, ttl: int = 600):
        """Edit an existing DNS record."""
        url = f"https://api.porkbun.com/api/json/v3/dns/edit/{domain}/{record_id}"
        data = {
            "apikey": self.api_key,
            "secretapikey": self.secret_key,
            "name": host,
            "type": rtype,
            "content": content,
            "ttl": ttl
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
