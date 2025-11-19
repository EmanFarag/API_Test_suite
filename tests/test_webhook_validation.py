import time
import pytest
import json
from datetime import datetime, timezone

import requests

from tests.test_api_workflow import client
from utils.webhook_utils import WebhookClient

client = WebhookClient()
test_payload = client.test_payload
token = client.webhook_token

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

    # Requested part to fetch uuid and validate the X-Correlation-ID in this specific payload
    uuid = last_request.get("uuid")
    x_correlation_id = payload["X-Correlation-ID"]
    assert uuid, "UUID missing from webhook payload"
    url = f"https://webhook.site/token/{x_correlation_id}/requests?query=uuid:{uuid}"
    response = requests.get(url)

    assert response.status_code == 200, f"API returned {response.status_code} for this {x_correlation_id}"
    assert response.json().get("data"), f"No requests found for UUID: {uuid}"

    assert "X-Correlation-ID" in payload, "X-Correlation-ID missing from webhook body"
    assert payload[
               "X-Correlation-ID"] == token, f"X-Correlation-ID mismatch. Expected: {token}, Got: {payload['X-Correlation-ID']}"

    # Validate timestamp is recent
    utc_now = datetime.now(timezone.utc)
    x_request_time = datetime.fromisoformat(x_request_time_str)
    delta = utc_now - x_request_time
    assert delta.total_seconds() <= 120, f"x-request-time older than 2 minutes ({delta})"
