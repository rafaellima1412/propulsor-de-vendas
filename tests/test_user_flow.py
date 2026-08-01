import pytest

pytestmark = pytest.mark.integration


def _register_form(**overrides):
    data = dict(
        username="joao.gerente",
        full_name="Joao Gerente",
        cpf="11144477735",
        password="senha-forte-123",
        role="gerente",
        novo_time="Time Alpha",
    )
    data.update(overrides)
    return data


def test_register_new_user_via_form(client):
    response = client.post("/user/register", data=_register_form())

    assert response.status_code == 201
    assert response.json() == {"message": "Usuário cadastrado com sucesso"}


def test_register_duplicate_cpf_shows_error_instead_of_crashing(client):
    client.post("/user/register", data=_register_form())

    response = client.post(
        "/user/register",
        data=_register_form(username="outro.usuario"),
    )

    assert response.status_code == 400
    assert "cadastrado" in response.json()["detail"].lower()


def test_login_with_correct_credentials_sets_cookie_and_returns_user(client):
    client.post("/user/register", data=_register_form())

    response = client.post(
        "/user/login",
        data={"username": "joao.gerente", "password": "senha-forte-123"},
    )

    assert response.status_code == 200
    assert response.json() == {"username": "joao.gerente", "role": "gerente"}
    assert "access_token" in response.cookies


def test_login_with_wrong_password_returns_401(client):
    client.post("/user/register", data=_register_form())

    response = client.post(
        "/user/login",
        data={"username": "joao.gerente", "password": "senha-errada"},
    )

    assert response.status_code == 401
    assert "access_token" not in response.cookies


def test_me_endpoint_requires_authentication(client):
    response = client.get("/user/me")

    assert response.status_code == 401


def test_authenticated_user_can_fetch_me(client):
    client.post("/user/register", data=_register_form())
    login = client.post(
        "/user/login",
        data={"username": "joao.gerente", "password": "senha-forte-123"},
    )
    client.cookies.set("access_token", login.cookies["access_token"])

    response = client.get("/user/me")

    assert response.status_code == 200
    assert response.json()["username"] == "joao.gerente"


def test_gerentes_endpoint_lists_created_manager(client):
    client.post("/user/register", data=_register_form())

    response = client.get("/user/gerentes")

    assert response.status_code == 200
    usernames = [u["username"] for u in response.json()]
    assert "joao.gerente" in usernames
