import logging
import requests
import yaml
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class APIClient:
    def __init__(self, settings_path: str = "config/settings.yml"):
        self.settings = self._load_settings(settings_path)
        self.base_url = self.settings["base_url"]
        self.test_data = self.settings["test_data"]

    def _load_settings(self, path: str):
        root = Path(__file__).resolve().parent.parent
        settings_file = root / path

        if not settings_file.exists():
            raise FileNotFoundError(f"settings.yml not found at {settings_file}")

        with open(settings_file, "r") as file:
            return yaml.safe_load(file)

    def post(self, endpoint: str, payload: dict):
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"POST {url} - payload={payload}")
            response = requests.post(url, json=payload)
            logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"POST request failed: {e}")
            raise

    def get(self, endpoint: str):
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"GET {url}")
            response = requests.get(url)
            logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"GET request failed: {e}")
            raise

    def delete(self, endpoint: str):
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"DELETE {url}")
            response = requests.delete(url)
            logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"DELETE request failed: {e}")
            raise
