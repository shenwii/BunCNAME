import requests
from typing import List, Dict, Any
from dns_provider import DNSProvider

class AdGuardHomeClient(DNSProvider):
    def __init__(self, base_url: str, username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)

    def _get(self, endpoint: str) -> Dict[str, Any]:
        response = self.session.get(f"{self.base_url}{endpoint}")
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        if data is None:
            data = {}
        response = self.session.post(f"{self.base_url}{endpoint}", json=data)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            # If response is not JSON, return empty dict
            return {}

    def get_records(self, domain: str) -> List[Dict[str, Any]]:
        """Retrieve DNS rewrite rules. For AdGuard Home, we treat rewrite rules as records."""
        result = self._get("/control/rewrite/list")
        if isinstance(result, list):
            rules = result
        else:
            rules = result.get("rules", [])
        # Filter rules that match the domain (exact match or subdomain)
        # But since domain is given, we assume all rules are for this "domain" context
        # AdGuard Home doesn't have domain-specific records like Porkbun
        # We need to adapt: treat all rules as if they are for the given domain
        records = []
        for rule in rules:
            domain_name = rule.get("domain")
            answer = rule.get("answer")
            # Only handle CNAME-like rules (answer is a domain, not IP)
            if self._is_domain(answer):
                # For AdGuard Home, host is the full domain_name if it ends with domain, else ignore?
                # Since AdGuard Home is global, we need to filter by domain
                if domain_name.endswith(f".{domain}") or domain_name == domain:
                    host = domain_name.replace(f".{domain}", "") if domain_name != domain else ""
                    records.append({
                        "id": f"{domain_name}=>{answer}",  # Unique ID
                        "name": domain_name,
                        "type": "CNAME",  # Assume CNAME
                        "content": answer,
                        "ttl": 600  # AdGuard Home doesn't have TTL for rewrites
                    })
        return records

    def create_record(self, domain: str, host: str, rtype: str, content: str, ttl: int = 600):
        """Create a DNS rewrite rule."""
        if rtype != "CNAME":
            raise ValueError("AdGuard Home only supports CNAME-like rewrites")
        full_domain = f"{host}.{domain}" if host else domain
        data = {
            "domain": full_domain,
            "answer": content
        }
        return self._post("/control/rewrite/add", data)

    def delete_record(self, domain: str, record_id: str):
        """Delete a DNS rewrite rule."""
        # record_id is "domain=>answer"
        domain_name, answer = record_id.split("=>", 1)
        data = {
            "domain": domain_name,
            "answer": answer
        }
        return self._post("/control/rewrite/delete", data)

    def edit_record(self, domain: str, record_id: str, host: str, rtype: str, content: str, ttl: int = 600):
        """Edit a DNS rewrite rule. Since AdGuard Home doesn't support edit, delete and create."""
        self.delete_record(domain, record_id)
        self.create_record(domain, host, rtype, content, ttl)

    def _is_domain(self, s: str) -> bool:
        """Check if string looks like a domain (not IP)."""
        # Simple check: if it contains letters and dots, assume domain
        return '.' in s and any(c.isalpha() for c in s)