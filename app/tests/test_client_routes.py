# app/tests/test_client_routes.py
def test_create_client(client):
    payload = {
        "name": "Samuel",
        "email": "samuel@example.com",
        "phone": "11999999999",
        "cpf": "12345678900",
        "address": "Rua Teste, 123",
        "city": "Brasília",
        "state": "DF",
        "postal_code": "70000000",
        "country": "Brasil",
        "password": "123456"
    }

    response = client.post("/clients", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "client_id" in body
    assert "access_tokens" in body
    assert body["tokens_type"] == "bearer"
    assert body["message"] == "Client successfully registered!"
