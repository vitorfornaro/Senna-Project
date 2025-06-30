def nif_validation(nif: str) -> bool:
    """
    Valida um NIF português (Número de Identificação Fiscal).
    Deve conter 9 dígitos e seguir o algoritmo de verificação da 9ª casa.
    """
    nif = nif.strip()
    
    if len(nif) != 9 or not nif.isdigit():
        return False

    # Converte os primeiros 8 dígitos em inteiros
    first_8_digits = [int(digit) for digit in nif[:8]]
    check_digit = int(nif[8])

    # Pesos fixos para cada posição
    weights = [9, 8, 7, 6, 5, 4, 3, 2]

    # Soma ponderada
    total = sum(w * d for w, d in zip(weights, first_8_digits))

    # Cálculo do dígito verificador
    remainder = total % 11
    calculated_digit = 0 if remainder in (0, 1) else 11 - remainder

    return check_digit == calculated_digit