from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DNSProvider(ABC):
    @abstractmethod
    def get_records(self, domain: str) -> List[Dict[str, Any]]:
        """Retrieve all DNS records for a domain."""
        pass

    @abstractmethod
    def create_record(self, domain: str, host: str, rtype: str, content: str, ttl: int = 600):
        """Create a new DNS record."""
        pass

    @abstractmethod
    def delete_record(self, domain: str, record_id: str):
        """Delete a DNS record by ID."""
        pass

    @abstractmethod
    def edit_record(self, domain: str, record_id: str, host: str, rtype: str, content: str, ttl: int = 600):
        """Edit an existing DNS record."""
        pass