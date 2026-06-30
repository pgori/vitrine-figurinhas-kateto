from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_lead_returns_created_card_with_assigned_seller(client: TestClient) -> None:
    response = client.post(
        "/leads",
        json={
            "name": "Yennefer",
            "desired_item": "Carta Geralt de Rivia",
            "phone": "(11) 99999-0000",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Yennefer"
    assert body["desired_item"] == "Carta Geralt de Rivia"
    assert body["phone"] == "11999990000"
    assert body["kanban_column"] == "Sem Contato"
    assert body["assigned_seller"]["name"] == "Marcelo"


def test_create_lead_rejects_implausible_phone(client: TestClient) -> None:
    response = client.post(
        "/leads",
        json={
            "name": "Triss",
            "desired_item": "Carta Ciri",
            "phone": "123",
        },
    )

    assert response.status_code == 400


def test_login_returns_bearer_token(client: TestClient) -> None:
    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/login",
        json={"username": "admin", "password": "senha-errada"},
    )

    assert response.status_code == 401


def test_list_leads_returns_authenticated_kanban_cards(client: TestClient) -> None:
    client.post(
        "/leads",
        json={
            "name": "Geralt",
            "desired_item": "Carta Yennefer",
            "phone": "11999990000",
        },
    )
    headers = _auth_headers(client)

    response = client.get("/leads", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Geralt"
    assert body[0]["kanban_column"] == "Sem Contato"
    assert body[0]["assigned_seller"]["name"] == "Marcelo"


def test_list_leads_requires_authentication(client: TestClient) -> None:
    response = client.get("/leads")

    assert response.status_code == 401


def test_list_leads_filters_by_column(client: TestClient) -> None:
    created = client.post(
        "/leads",
        json={
            "name": "Ciri",
            "desired_item": "Carta Triss",
            "phone": "11999990000",
        },
    ).json()
    headers = _auth_headers(client)

    client.patch(
        f"/leads/{created['id']}",
        json={"kanban_column": "Finalizado"},
        headers=headers,
    )

    response = client.get("/leads?column=Finalizado", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["kanban_column"] == "Finalizado"


def test_move_lead_updates_kanban_column(client: TestClient) -> None:
    created = client.post(
        "/leads",
        json={
            "name": "Dandelion",
            "desired_item": "Carta Zoltan",
            "phone": "11999990000",
        },
    ).json()
    headers = _auth_headers(client)

    response = client.patch(
        f"/leads/{created['id']}",
        json={"kanban_column": "Em Contato"},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["kanban_column"] == "Em Contato"


def test_move_lead_returns_404_for_missing_card(client: TestClient) -> None:
    response = client.patch(
        "/leads/999",
        json={"kanban_column": "Perdido"},
        headers=_auth_headers(client),
    )

    assert response.status_code == 404


def test_move_lead_rejects_invalid_column(client: TestClient) -> None:
    created = client.post(
        "/leads",
        json={
            "name": "Zoltan",
            "desired_item": "Carta Dandelion",
            "phone": "11999990000",
        },
    ).json()

    response = client.patch(
        f"/leads/{created['id']}",
        json={"kanban_column": "Arquivado"},
        headers=_auth_headers(client),
    )

    assert response.status_code == 400


def _auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/login",
        json={"username": "admin", "password": "admin"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

