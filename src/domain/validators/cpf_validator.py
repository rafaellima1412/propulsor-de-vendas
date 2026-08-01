def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_digito(cpf_part, peso):
        soma = sum(int(num) * fator for num, fator in zip(cpf_part, range(peso, 1, -1), strict=True))
        resto = (soma * 10) % 11
        return resto if resto < 10 else 0

    digito1 = calc_digito(cpf[:9], 10)
    digito2 = calc_digito(cpf[:10], 11)
    return cpf[-2:] == f"{digito1}{digito2}"