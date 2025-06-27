# 🇵🇹 Senna Project

Mapa de Responsabilidades Extractor

This project automates the extraction of structured financial data from encrypted *Mapas de Responsabilidades* PDFs in Portugal. It uses regular expressions, PDF parsing, and business rules to classify and export client profiles.

---

## 📁 Project Structure

```bash
Senna-Project/
│
├── src/
│   ├── main.py                   # Main pipeline script
│   ├── config.py                 # Directory and folder configs
│   ├── pdf_decryptor.py          # Decrypts encrypted PDFs
│   ├── pdf_text_extractor.py     # Extracts raw text from PDFs
│   ├── pdf_data_extractor.py     # Parses text and applies regex
│   ├── pdf_output_handler.py     # Outputs CSV and JSON (by client and full)
│   ├── dadosCliente.py           # Manual client saving script (optional)
│   └── utils/                    # Auxiliary functions (e.g., validation)
│
├── maps/
│   ├── encrypted/                # Encrypted input PDFs
│   ├── decrypted/                # Decrypted PDFs
│   ├── decrypted/processed/     # Decrypted PDFs already processed
│   └── outputs/
│       ├── csv/resultado_extracao.csv
│       └── json/resultado_extracao.json
│
├── customers/                   # JSON exports split by NIF (one file per client)
├── logs/
│   └── unprocessed_pdfs.log     # Log file for PDFs with parsing issues
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker setup file
├── README.md                    # Project documentation
```

## 🎯 Features

- ✅ Decrypts protected PDFs using `pikepdf`
- ✅ Extracts text using `PyPDF2`
- ✅ Parses with complex regular expressions
- ✅ Extracts key fields: NIF, bank, amount, guarantees, status
- ✅ Detects guarantees including edge cases like dashes (`-`)
- ✅ Applies business rules:
  - `perfil_individual`: No guarantees, not in litigation, and from institution without any other guarantees
  - `perfila`: If cumulative eligible debt ≥ 6000 €
- ✅ Exports:
  - Full CSV with all extracted data
  - Full JSON with all rows
  - One JSON file per client (by NIF)
- ✅ Logs unprocessable PDFs
- ✅ Works via Python or Docker

---

## 🚀 How to Run (Locally)

### 1. Create virtual environment (recommended)

bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

### 2. Install requirements

pip install -r requirements.txt

### 3. Add PDFs to process
Place encrypted PDFs into:
maps/encrypted/

### 4. Run the project
python src/main.py

🐳 How to Run with Docker

### 1. Build the Docker image

docker build -t senna-app .

### 2. Run the container

docker run --rm \
  -v $(pwd)/maps:/app/maps \
  -v $(pwd)/customers:/app/customers \
  -v $(pwd)/logs:/app/logs \
  senna-app

  On Windows (CMD or PowerShell), replace $(pwd) with %cd% or the full path.


### 📦 Outputs
	•	✅ resultado_extracao.csv: full dataset
	•	✅ resultado_extracao.json: full dataset
	•	✅ customers/{nif}.json: one JSON per client
	•	🧾 logs/unprocessed_pdfs.log: list of PDFs that couldn’t be parsed


### 🧠 Business Logic Highlights
	•	Guarantees (garantias) are parsed from variable table formats.
	•	Guarantees with - or missing values are treated as 0.0.
	•	If a client has at least one eligible product and total eligible debt ≥ 6000 €, they are flagged as perfila = True.

 ### 🧰 Tech Stack
	•	Python 3.8+
	•	pikepdf, PyPDF2, pandas, re
	•	Docker (optional deployment)

### 🧪 Example Run Output

✅ PDFs processed successfully!
📁 Customers JSON saved to: customers/{nif}.json
📄 CSV generated at: maps/outputs/csv/resultado_extracao.csv
❗ Logged 2 unprocessable PDFs to logs/unprocessed_pdfs.log

### 🛠️ Git Commands

git add .
git commit -m "feat: add Docker and JSON by client support"
git push origin main

### 👨‍💼 Author


Maintained by Lucas Inocencio // Originally created by Vitor Fornaro