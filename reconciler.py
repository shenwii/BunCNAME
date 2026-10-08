import logging
from typing import List, Dict, Any
from dns_provider import DNSProvider

logger = logging.getLogger(__name__)


class Reconciler:
    def __init__(self, clients: Dict[str, DNSProvider]):
        self.clients = clients

    def sync_config(self, config: List[Dict[str, Any]]):
        for domain_entry in config:
            domain = domain_entry.get("domain")
            providers = domain_entry.get("providers")
            desired_records = domain_entry.get("records", [])

            if not domain or not providers:
                logger.warning("Skipping entry without domain or provider field")
                continue

            if isinstance(providers, str):
                providers = [providers]  # 兼容旧格式

            for provider in providers:
                if provider not in self.clients:
                    logger.warning(f"Provider {provider} not configured, skipping")
                    continue

                client = self.clients[provider]
                logger.info(f"Syncing records for domain: {domain} with provider: {provider}")
                self._sync_domain(client, domain, desired_records)

    def _sync_domain(self, client: DNSProvider, domain: str, desired_records: List[Dict[str, Any]]):
        try:
            remote_records = client.get_records(domain)
        except Exception as e:
            logger.error(f"Failed to fetch remote records for {domain}: {e}")
            return

        logger.info(f"Found {len(remote_records)} remote records for {domain}")

        # Filter remote records to only include CNAME records (since this tool manages CNAMEs)
        remote_map = {}
        for r in remote_records:
            rtype = r.get('type', 'CNAME').upper()  # Normalize to uppercase
            if rtype != 'CNAME':
                continue  # Skip non-CNAME records
            name = r.get('name', '')
            if name == domain:
                host = ''
            else:
                host = name.replace(f".{domain}", "")

            key = (host, rtype)
            remote_map[key] = r
            logger.debug(f"Remote CNAME record: {host}.{domain} [{rtype}] -> {r.get('content', '')}")

        logger.info(f"Found {len(remote_records)} remote records for {domain}, {len(remote_map)} are CNAME records")

        desired_map = {}
        for r in desired_records:
            rtype = r.get('type', 'CNAME').upper()  # Normalize to uppercase
            if rtype != 'CNAME':
                continue  # Skip non-CNAME records in config
            host = r.get('host', '')
            key = (host, rtype)
            desired_map[key] = r
            logger.debug(f"Desired CNAME record: {host}.{domain} [{rtype}] -> {r.get('content', '')}")

        logger.info(f"Found {len(remote_records)} remote records for {domain}, {len(remote_map)} are CNAME records")

        logger.info(f"Will process {len(desired_map)} desired CNAME records, {len(remote_map)} remote CNAME records")

        # 1. Delete records that are on remote but NOT in desired
        for key, remote_rec in remote_map.items():
            if key not in desired_map:
                logger.info(f"Deleting remote record: {key[0]}.{domain} [{key[1]}]")
                try:
                    client.delete_record(domain, remote_rec['id'])
                except Exception as e:
                    logger.error(f"Failed to delete record {remote_rec['id']}: {e}")

        # 2. Create or Update records
        for key, desired_rec in desired_map.items():
            host = key[0]
            rtype = key[1]
            content = desired_rec.get('content')
            ttl = int(desired_rec.get('ttl', 600))

            if key in remote_map:
                remote_rec = remote_map[key]
                needs_update = (
                    remote_rec['content'] != content or
                    int(remote_rec.get('ttl', 600)) != ttl
                )
                if needs_update:
                    logger.info(f"Updating record: {host}.{domain} [{rtype}]")
                    try:
                        client.edit_record(domain, remote_rec['id'], host, rtype, content, ttl)
                    except Exception as e:
                        logger.error(f"Failed to update record {remote_rec['id']}: {e}")
                else:
                    logger.debug(f"Record in sync: {host}.{domain}")
            else:
                logger.info(f"Creating record: {host}.{domain} [{rtype}]")
                try:
                    client.create_record(domain, host, rtype, content, ttl)
                except Exception as e:
                    logger.error(f"Failed to create record: {e}")
