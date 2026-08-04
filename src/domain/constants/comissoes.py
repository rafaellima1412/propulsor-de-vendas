from src.domain.enums.enums import PlanoInternet

COMISSAO_POR_PLANO: dict[str, float] = {
    PlanoInternet.MB_500.value: 15.0,
    PlanoInternet.GB_1.value: 25.0,
    PlanoInternet.GB_2.value: 40.0,
    PlanoInternet.GB_10.value: 70.0,
}