# 🏎️ Senna-Project

**Senna-Project** is a system for processing and profiling **Credit Responsibility Reports (MDR)** in a cryptography PDF format.  
It handles **decryption, text extraction with OCR fallback, data structuring, business rule profiling (Senninha)**, and exports results in **JSON, CSV**, or via a **Flask API**.

---

## 🚀 Features

- 🔓 **Automatic PDF decryption**
- 📝 **Text extraction** with **OCR (Tesseract) fallback**
- 📊 **Structured data parsing** with Pandas
- 🧠 **Business rule profiling** through `Senninha`
- 💾 **Multiple export formats**:
  - JSON (global)
  - JSON per client
  - CSV
- 🌐 **Flask API** ready for integration with **n8n** or external apps
- 🗂️ **Modular architecture** (Services, Handlers, Utils, API)

---

## 📂 Project Structure

```bash
senna-project/
│── customers/              # Output per client
│── logs/                   # Execution logs
│── maps/                   # Processed PDFs
│── docs/development/       # Jupyter notebooks and technical docs
│   └── all_in_one.ipynb
│── senna-project/
│   └── src/
│       ├── api/            # Flask API
│       │   └── app.py
│       ├── handlers/       # Output and validation handlers
│       │   ├── pdf_output_handler.py
│       │   └── validador.py
│       ├── services/       # Core processing and business rules
│       │   ├── pdf_data_extractor.py
│       │   ├── pdf_decryptor.py
│       │   ├── pdf_text_extractor.py
│       │   └── senninha.py
│       ├── utils/          # Helper functions
│       └── main.py         # Batch execution
│── bancos_padrao.csv       # Bank reference table
│── requirements.txt        # Dependencies
│── README.md               # Documentation

 ```

⚙️ Setup & Installation

1. Clone repository

```bash
git clone https://github.com/vitorfornaro/Senna-Project.git
cd Senna-Project
 ```

2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
 ```

3. Install dependencies

```bash
pip install -r requirements.txt
 ```

▶️ How to Run
🔹 Batch Processing
```bash
make start
# or directly:
python senna-project/src/main.py
 ```
🔹 Run Flask API
```bash
make api
# or directly:
python senna-project/src/api/app.py
 ```
 🔹 Run Streamlit
```bash
make streamlit
# or directly:
streamlit run app_streamlit.py
 ```

API will be available at:
```bash
http://localhost:5001/perfilamento
 ```
📡 API Example

Request
```bash
curl -X POST http://localhost:5001/perfilamento \
  -F "mdr=@/path/to/file.pdf"
 ```
Response
```bash
{
  "nome": "joaosilva",
  "nif": "123456789",
  "perfila": true,
  "pari_persi": true,
  "info_institutions": [
    {
      "instituicao": "Banco X",
      "divida": 12000.0,
      "garantias": 0,
      "litigio": 0,
      "perfila": true
    }
  ]
}
 ```
🧠 Profiling Rules (Senninha)

Business Rules 

👨‍💻 Authors

Lucas Inocênico e Vitor Fornaro

---

👉 Do you want me to **create this README.md file directly in your repo** (so you just commit and push), or just leave it here for you to copy-paste into GitHub?