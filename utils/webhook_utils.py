import logging
import os
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(handler)


class WebhookClient:
    def __init__(self, payload=None, timeout_seconds=120):
        self.webhook_url = os.environ.get("WEBHOOK_URL")
        self.webhook_token = os.environ.get("WEBHOOK_TOKEN")
        self.timeout_seconds = timeout_seconds
        self.test_payload = payload or {
            "event": "test_event",
            "data": "sample data"
        }

        if not self.webhook_url:
            raise ValueError("WEBHOOK_URL environment variable not set")
        if not self.webhook_token:
            raise ValueError("WEBHOOK_TOKEN environment variable not set")

    def send_webhook(self, payload=None):
        """Send POST webhook with x-request-time header."""
        payload = payload or self.test_payload
        utc_now = datetime.now(timezone.utc)

        headers = {
            "Content-Type": "application/json",
            "x-request-time": utc_now.isoformat()
        }

        logger.info(f"POST → {self.webhook_url} | payload={payload}")
        response = requests.post(
            self.webhook_url,
            json=payload,
            headers=headers,
            allow_redirects=False,
            timeout=self.timeout_seconds
        )
        response.raise_for_status()

        return headers["x-request-time"]

    def fetch_webhook_requests(self, retries=10, delay=1):
        """Fetch webhook requests from Webhook.site API."""
        api_url = f"https://webhook.site/token/{self.webhook_token}/requests"

        for attempt in range(retries):
            logger.info(f"Fetching webhook requests (attempt {attempt + 1})")

            response = requests.get(api_url, timeout=self.timeout_seconds)
            response.raise_for_status()

            data = response.json()

            # ✔ Webhook.site always wraps list inside "data"
            events = data.get("data", [])

            if isinstance(events, list) and events:
                return events

            time.sleep(delay)

        return []