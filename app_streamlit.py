import streamlit as st
import requests
import json
from pathlib import Path

# ==== CONFIGURAÇÕES ====
st.set_page_config(page_title="Senna - Pré-venda", layout="centered")
st.title("📄 Análise de Mapa de Responsabilidades")
st.write("Faça o upload de um PDF e veja se o cliente perfilou!")

# ==== CAMINHO DO CONTADOR ====
CONTADOR_PATH = Path("contador.json")

# ==== FUNÇÕES DE CONTADOR ====
def carregar_contador():
    if CONTADOR_PATH.exists():
        with open(CONTADOR_PATH, "r") as f:
            return json.load(f)
    return {"perfilado": 0, "nao_perfilado": 0}

def salvar_contador(data):
    with open(CONTADOR_PATH, "w") as f:
        json.dump(data, f, indent=2)

# ==== CARREGAR CONTADOR ====
contador = carregar_contador()

# ==== UPLOAD ====
uploaded_file = st.file_uploader("📎 Envie o Mapa de Responsabilidades (.pdf)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("⏳ Enviando para o motor Senna..."):
        try:
            # Prepara o arquivo para envio
            files = {
                "mdr": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
            }

            # Envia para o endpoint do n8n (webhook de teste ou produção)
            response = requests.post("http://localhost:5678/webhook-test/webhook-mdr", files=files)

            # Mostra o conteúdo bruto da resposta (para debug)
            st.code(response.text, language="json")

            # ⚠️ Carrega a resposta JSON como dicionário Python
            result = response.json()

            # Feedback visual
            st.success("✅ Processado com sucesso!")
            st.subheader("📄 Resultado do Perfilamento")
            st.json(result)

            # Extrair informações principais
            nif = result.get("nif", "Desconhecido")
            mesmapa = result.get("mesmapa", "Desconhecido")
            perfilado = result.get("perfilado", False)

            st.markdown(f"- **NIF**: `{nif}`")
            st.markdown(f"- **Mês do mapa**: `{mesmapa}`")

            if perfilado:
                st.success("🎯 Este cliente **perfilou!**")
                contador["perfilado"] += 1
            else:
                st.warning("❌ Este cliente **não perfilou.**")
                contador["nao_perfilado"] += 1

            # Atualiza contador local
            salvar_contador(contador)

        except Exception as e:
            st.error(f"❌ Erro ao processar o PDF: {e}")

# ==== VISUALIZAÇÃO DO CONTADOR ====
st.divider()
st.subheader("📊 Estatísticas Gerais")
col1, col2 = st.columns(2)
col1.metric("Perfilados", contador["perfilado"])
col2.metric("Não perfilados", contador["nao_perfilado"])