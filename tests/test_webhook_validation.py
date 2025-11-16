import time
import pytest
import json
from datetime import datetime, timezone
from utils.webhook_utils import WebhookClient

client = WebhookClient()
test_payload = client.test_payload

@pytest.fixture
def send_test_webhook():
    timestamp = client.send_webhook()
    return timestamp


def test_webhook_received(send_test_webhook):
    sent_timestamp = send_test_webhook
    max_wait_time = 10  # Maximum seconds to wait
    wait_interval = 0.5  # Check every 0.5 seconds
    last_request = None
    x_request_time_str = None

    # Wait for the new webhook request to appear
    for _ in range(int(max_wait_time / wait_interval)):
        requests_list = client.fetch_webhook_requests()

        if requests_list:
            last_request = requests_list[-1]
            headers = last_request.get("headers", {})
            x_request_time_value = headers.get("x-request-time")

            if x_request_time_value:
                if isinstance(x_request_time_value, list):
                    x_request_time_str = x_request_time_value[0]
                else:
                    x_request_time_str = x_request_time_value

                # Check if this is our newly sent request
                if x_request_time_str == sent_timestamp:
                    break

        time.sleep(wait_interval)
    else:
        pytest.fail("Webhook request not received within timeout period")

    # Validate the payload and headers
    raw_content = last_request.get("content")
    try:
        payload = json.loads(raw_content) if raw_content else {}
    except json.JSONDecodeError:
        payload = {}

    # Validate payload keys + values
    for key, value in test_payload.items():
        assert key in payload, f"{key} missing from webhook payload"
        assert payload[key] == value, f"{key} mismatch"

        # Validate timestamp is recent
        utc_now = datetime.now(timezone.utc)
        x_request_time = datetime.fromisoformat(x_request_time_str)
        delta = utc_now - x_request_time
        assert delta.total_seconds() <= 120, f"x-request-time older than 2 minutes ({delta})"