def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_development_cors_allows_local_vite_ports_only(client):
    allowed = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://127.0.0.1:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5174"

    rejected = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://example.com:5174",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in rejected.headers
