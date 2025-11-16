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
    utc_now = datetime.now(timezone.utc)
    time.sleep(5)
    requests_list = client.fetch_webhook_requests()

    assert isinstance(requests_list, list), "Webhook API did not return a list of events"
    assert len(requests_list) > 0, "No webhook requests received"

    # The newest entry is index -1
    last_request = requests_list[-1]

    # Extract content from the webhook
    raw_content = (
        last_request.get("content")
    )
    try:
        payload = json.loads(raw_content) if raw_content else {}
    except json.JSONDecodeError:
        payload = {}

    # Get Headers from webhook
    headers = last_request.get("headers", {})

    # Validate payload keys + values
    for key, value in test_payload.items():
        assert key in payload, f"{key} missing from webhook payload"
        assert payload[key] == value, f"{key} mismatch"

    # Validate custom timestamp in header
    x_request_time_value = headers.get("x-request-time")
    assert x_request_time_value is not None, "Missing x-request-time header"

    if isinstance(x_request_time_value, list):
        x_request_time_str = x_request_time_value[0]
    else:
        x_request_time_str = x_request_time_value

    x_request_time = datetime.fromisoformat(x_request_time_str)

    delta = utc_now - x_request_time
    assert delta.total_seconds() <= 120, f"x-request-time older than 2 minutes ({delta})"