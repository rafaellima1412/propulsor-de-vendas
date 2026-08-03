import pytest

pytestmark = pytest.mark.integration


def _admin_form(**overrides):
    data = dict(
        username="admin.raiz",
        full_name="Admin Raiz",
        cpf="52998224725",
        password="senha-admin-123",
        role="admin",
    )
    data.update(overrides)
    return data


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


def _bootstrap_admin(client):
    """Cadastra o primeiro usuário do sistema (sempre nasce admin, por
    bootstrap) e autentica o client com o cookie dele, para poder cadastrar
    os demais papéis nos testes que precisam disso."""
    client.post("/user/register", json=_admin_form())
    login = client.post("/user/login", json={"username": "admin.raiz", "password": "senha-admin-123"})
    client.cookies.set("access_token", login.cookies["access_token"])


def test_bootstrap_first_user_becomes_admin_regardless_of_requested_role(client):
    """O caminho de bootstrap ignora o role pedido no formulário — senão
    bastaria ser o primeiro a se cadastrar como "coordenador" pra furar a
    regra de que só admin cria os demais papéis."""
    response = client.post("/user/register", json=_register_form())  # pede "gerente"
    assert response.status_code == 201

    login = client.post("/user/login", json={"username": "joao.gerente", "password": "senha-forte-123"})
    assert login.json()["role"] == "admin"


def test_register_without_admin_session_is_rejected_after_bootstrap(client):
    _bootstrap_admin(client)
    client.cookies.clear()

    response = client.post("/user/register", json=_register_form(username="sem.sessao"))

    assert response.status_code == 403


def test_register_new_user_via_form(client):
    _bootstrap_admin(client)

    response = client.post("/user/register", json=_register_form())

    assert response.status_code == 201
    assert response.json() == {"message": "Usuário cadastrado com sucesso"}


def test_register_duplicate_cpf_shows_error_instead_of_crashing(client):
    _bootstrap_admin(client)
    client.post("/user/register", json=_register_form())

    response = client.post(
        "/user/register",
        json=_register_form(username="outro.usuario"),
    )

    assert response.status_code == 400
    assert "cadastrado" in response.json()["detail"].lower()


def test_login_with_correct_credentials_sets_cookie_and_returns_user(client):
    _bootstrap_admin(client)
    client.post("/user/register", json=_register_form())

    response = client.post(
        "/user/login",
        json={"username": "joao.gerente", "password": "senha-forte-123"},
    )

    assert response.status_code == 200
    assert response.json() == {"username": "joao.gerente", "role": "gerente"}
    assert "access_token" in response.cookies


def test_login_with_wrong_password_returns_401(client):
    _bootstrap_admin(client)
    client.post("/user/register", json=_register_form())

    response = client.post(
        "/user/login",
        json={"username": "joao.gerente", "password": "senha-errada"},
    )

    assert response.status_code == 401
    assert "access_token" not in response.cookies


def test_me_endpoint_requires_authentication(client):
    response = client.get("/user/me")

    assert response.status_code == 401


def test_authenticated_user_can_fetch_me(client):
    _bootstrap_admin(client)
    client.post("/user/register", json=_register_form())
    login = client.post(
        "/user/login",
        json={"username": "joao.gerente", "password": "senha-forte-123"},
    )
    client.cookies.set("access_token", login.cookies["access_token"])

    response = client.get("/user/me")

    assert response.status_code == 200
    assert response.json()["username"] == "joao.gerente"


def test_gerentes_endpoint_lists_created_manager(client):
    _bootstrap_admin(client)
    client.post("/user/register", json=_register_form())

    response = client.get("/user/gerentes")

    assert response.status_code == 200
    usernames = [u["username"] for u in response.json()]
    assert "joao.gerente" in usernames