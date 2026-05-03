from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_echo():
    response = client.post("/echo", json={"input": "Test"})
    assert response.status_code == 200
    assert response.json() == {"output": "Test"}
