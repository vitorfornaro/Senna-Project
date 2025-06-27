import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MAPS_DIR = os.path.join(BASE_DIR, "..", "maps")

    # Pastas fonte e destino
    ENCRYPTED_FOLDER = os.path.join(MAPS_DIR, "encrypted")
    DECRYPTED_FOLDER = os.path.join(MAPS_DIR, "decrypted")
    PROCESSED_ENCRYPTED_FOLDER = os.path.join(ENCRYPTED_FOLDER, "processed")
    PROCESSED_DECRYPTED_FOLDER = os.path.join(DECRYPTED_FOLDER, "processed")

    # Pastas para os outputs
    OUTPUT_FOLDER = os.path.join(MAPS_DIR, "outputs")
    CSV_OUTPUT = os.path.join(OUTPUT_FOLDER, "csv")
    JSON_OUTPUT = os.path.join(OUTPUT_FOLDER, "json")
    CUSTOMERS_OUTPUT = os.path.join(MAPS_DIR, "customers")

    # Criar pastas se não existirem
    for folder in [
        ENCRYPTED_FOLDER,
        DECRYPTED_FOLDER,
        PROCESSED_ENCRYPTED_FOLDER,
        PROCESSED_DECRYPTED_FOLDER,
        OUTPUT_FOLDER,
        CSV_OUTPUT,
        JSON_OUTPUT,
        CUSTOMERS_OUTPUT
    ]:
        os.makedirs(folder, exist_ok=True)