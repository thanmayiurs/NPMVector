from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "NPMVector API is running"


def test_packages_versions_endpoint():
    response = client.get("/packages/react/versions")
    assert response.status_code == 200
    assert "versions" in response.json()
    assert isinstance(response.json()["versions"], list)
