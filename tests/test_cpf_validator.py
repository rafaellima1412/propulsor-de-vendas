import pytest

from src.domain.validators.cpf_validator import validar_cpf

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "cpf",
    [
        "111.444.777-35",  # classic valid sample CPF, with punctuation
        "11144477735",  # same CPF, digits only
    ],
)
def test_valid_cpf_is_accepted(cpf):
    assert validar_cpf(cpf) is True


@pytest.mark.parametrize(
    "cpf",
    [
        "11144477736",  # wrong check digits
        "111.444.777-36",
        "00000000000",  # all repeated digits
        "11111111111",
        "123",  # too short
        "123456789012345",  # too long
        "",
    ],
)
def test_invalid_cpf_is_rejected(cpf):
    assert validar_cpf(cpf) is False
