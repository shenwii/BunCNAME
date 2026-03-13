import os
import time
import logging
from dotenv import load_dotenv
from porkbun_client import PorkbunClient
from adguard_home_client import AdGuardHomeClient
from reconciler import Reconciler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()

    # Porkbun credentials
    api_key = os.getenv("PORKBUN_API_KEY")
    secret_key = os.getenv("PORKBUN_SECRET_KEY")

    # AdGuard Home credentials
    adguard_url = os.getenv("ADGUARD_HOME_URL")
    adguard_username = os.getenv("ADGUARD_HOME_USERNAME")
    adguard_password = os.getenv("ADGUARD_HOME_PASSWORD")

    config_path = os.getenv("CONFIG_PATH", "records.json")
    interval = int(os.getenv("SYNC_INTERVAL", "30")) # In minutes

    clients = {}
    if api_key and secret_key:
        clients["porkbun"] = PorkbunClient(api_key, secret_key)
    else:
        logger.warning("PORKBUN_API_KEY and PORKBUN_SECRET_KEY not set, skipping Porkbun")

    if adguard_url:
        clients["adguard_home"] = AdGuardHomeClient(adguard_url, adguard_username, adguard_password)
    else:
        logger.warning("ADGUARD_HOME_URL not set, skipping AdGuard Home")

    if not clients:
        logger.error("No DNS providers configured.")
        return

    reconciler = Reconciler(clients, config_path)

    logger.info(f"Starting BunCNAME sync loop. Interval: {interval} minutes.")
    
    while True:
        logger.info("Starting sync cycle...")
        try:
            reconciler.sync()
            logger.info("Sync cycle completed.")
        except Exception as e:
            logger.error(f"Error during sync cycle: {e}")

        logger.info(f"Waiting {interval} minutes for next cycle...")
        time.sleep(interval * 60)

if __name__ == "__main__":
    main()
