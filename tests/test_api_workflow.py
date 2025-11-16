import pytest
from utils.api_client import APIClient

client = APIClient()

@pytest.fixture
def data():
    return client.test_data

@pytest.mark.parametrize(
    "resource_payload,expected_status",
    [
        ("valid_resource_creation", 201),
        ("invalid_resource_with_missing_title_field", 201),  # JSONPlaceholder accepts anything
        ("invalid_resource_with_empty_body", 201),
    ],
)
def test_create_resource(resource_payload, expected_status, data):
    payload = data[resource_payload]
    response = client.post("/posts", payload)
    assert response.status_code == expected_status
    assert "id" in response.json()

@pytest.mark.parametrize(
    "resource_id_payload,expected_status",
    [
        ("valid_resource_id", 200),
        ("invalid_resource_id", 404),
    ],
)
def test_get_resource_by_id(resource_id_payload, expected_status, data):
    payload = data[resource_id_payload]
    response = client.get(f"/posts/{payload}")
    assert response.status_code == expected_status


def test_delete_resource_by_id(data):
    create_response = client.post("/posts", data["valid_resource_creation"])
    created_id = create_response.json().get("id")

    response = client.delete(f"/posts/{created_id}")
    assert response.status_code == 200
