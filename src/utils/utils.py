def nif_validation(nif: str) -> bool:
    if len(nif) != 9 or not nif.isdigit():
        return False
    
    first_8_digit = [int(digit) for digit in nif[:8]]

    check_digit = int(nif[8])

    weights = [9, 8, 7, 6, 5, 4, 3, 2]
    
    total = sum(p * d for p, d in zip(weights, first_8_digit))
    
    remainder = total % 11
    calculated_digit = 11 - remainder if remainder != 0 else 0

    return check_digit == calculated_digit