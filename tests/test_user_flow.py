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
    response = client.post("/user/register", data=_register_form(), follow_redirects=False)

    # The route redirects back to the register page on success.
    assert response.status_code == 302
    assert response.headers["location"] == "/user/register"


def test_register_duplicate_cpf_shows_error_instead_of_crashing(client):
    client.post("/user/register", data=_register_form())

    response = client.post(
        "/user/register",
        data=_register_form(username="outro.usuario"),
    )

    assert response.status_code == 200
    assert "j\u00e1 est\u00e1 cadastrado" in response.text.lower() or "cadastrado" in response.text.lower()


def test_login_with_correct_credentials_sets_cookie_and_redirects(client):
    client.post("/user/register", data=_register_form())

    response = client.post(
        "/user/cadastro",
        data={"username": "joao.gerente", "password": "senha-forte-123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == "/pagina/inicial"
    assert "access_token" in response.cookies


def test_login_with_wrong_password_shows_login_form_again(client):
    client.post("/user/register", data=_register_form())

    response = client.post(
        "/user/cadastro",
        data={"username": "joao.gerente", "password": "senha-errada"},
    )

    # NOTE: login.html doesn't currently render the `error` message the
    # route passes it (tracked as a known issue - see README). What we can
    # verify today is that a wrong password does NOT log the user in: no
    # redirect, no access_token cookie, same login form re-rendered.
    assert response.status_code == 200
    assert "access_token" not in response.cookies
    assert "<form" in response.text.lower()


def test_register_page_requires_authentication(client):
    response = client.get("/user/register", follow_redirects=False)

    assert response.status_code == 401


def test_authenticated_user_can_load_register_page(client):
    client.post("/user/register", data=_register_form())
    login = client.post(
        "/user/cadastro",
        data={"username": "joao.gerente", "password": "senha-forte-123"},
        follow_redirects=False,
    )
    client.cookies.set("access_token", login.cookies["access_token"])

    response = client.get("/user/register")

    assert response.status_code == 200


def test_gerentes_endpoint_lists_created_manager(client):
    client.post("/user/register", data=_register_form())

    response = client.get("/user/gerentes")

    assert response.status_code == 200
    usernames = [u["username"] for u in response.json()]
    assert "joao.gerente" in usernames