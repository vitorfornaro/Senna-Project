import os
import json
import requests
import streamlit as st
from pathlib import Path

# ==== CONFIG ====
st.set_page_config(page_title="Senna - Pré-venda", layout="centered")
st.title("📄 Análise de Mapa de Responsabilidades")
st.write("Faça o upload de um PDF e veja se o cliente perfilou!")

# Onde roda o Streamlit?
RUN_ENV = st.sidebar.selectbox("Rodando Streamlit em:", ["Host (venv)", "Docker"], index=0)

# Qual webhook usar?
MODE = st.sidebar.radio("Webhook do n8n:", ["Produção (/webhook)", "Teste (/webhook-test)"], index=0)

# Caminho/nome do arquivo no webhook (CONFIRA com seu fluxo n8n)
FILE_FIELD = st.sidebar.text_input("Nome do campo do arquivo no n8n", value="mdr")

# Monta base URL
if RUN_ENV == "Host (venv)":
    BASE = "http://localhost:5678"
else:
    BASE = "http://n8n:5678"   # nome do serviço no docker-compose

PATH = "/webhook/webhook-mdr" if MODE.startswith("Produção") else "/webhook-test/webhook-mdr"
URL = f"{BASE}{PATH}"

st.caption(f"📡 Endpoint atual: `{URL}`  | Campo do arquivo: `{FILE_FIELD}`")

# ==== CAMINHO DO CONTADOR ====
CONTADOR_PATH = Path("contador.json")

def carregar_contador():
    if CONTADOR_PATH.exists():
        with open(CONTADOR_PATH, "r") as f:
            return json.load(f)
    return {"perfilado": 0, "nao_perfilado": 0}

def salvar_contador(data):
    with open(CONTADOR_PATH, "w") as f:
        json.dump(data, f, indent=2)

contador = carregar_contador()

# ==== UPLOAD ====
uploaded_file = st.file_uploader("📎 Envie o Mapa de Responsabilidades (.pdf)", type=["pdf"])

def pick_bool(d, *paths, default=False):
    """Busca um boolean em possíveis caminhos ('a', 'a.b', 'a.b.c')."""
    for p in paths:
        cur = d
        ok = True
        for k in p.split("."):
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, (bool, int)):
            return bool(cur)
    return default

if uploaded_file is not None:
    with st.spinner("⏳ Enviando para o motor Senna..."):
        try:
            files = {FILE_FIELD: (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(URL, files=files, timeout=120)

            st.write("**HTTP status:**", response.status_code)
            if not response.ok:
                st.error("❌ Requisição não OK. Veja o corpo abaixo:")
                st.code(response.text, language="json")
                st.stop()

            # Tenta decodificar JSON
            try:
                result = response.json()
            except Exception:
                st.error("❌ Resposta não é JSON. Corpo recebido:")
                st.code(response.text)
                st.stop()

            st.success("✅ Processado com sucesso!")
            st.subheader("📄 Resultado do Perfilamento (JSON bruto)")
            st.json(result)

            # Fallback de campos comuns no Senna
            nif = result.get("nif") or result.get("user", {}).get("nif") or "Desconhecido"
            mesmapa = (
                result.get("mesmapa")
                or result.get("mapa_mes")
                or result.get("user", {}).get("mesmapa")
                or "Desconhecido"
            )

            # Chave do perfilamento: tenta vários locais/nomes
            perfilado = pick_bool(
                result,
                "perfilado",          # seu código atual
                "perfila",            # nome usado em fases anteriores
                "perfil.perfila",     # dentro de um bloco "perfil"
                "perfil.perfilado",
                "perfil_individual",  # variação
            )

            st.markdown(f"- **NIF**: `{nif}`")
            st.markdown(f"- **Mês do mapa**: `{mesmapa}`")

            if perfilado:
                st.success("🎯 Este cliente **perfilou!**")
                contador["perfilado"] += 1
            else:
                st.warning("❌ Este cliente **não perfilou.**")
                contador["nao_perfilado"] += 1

            salvar_contador(contador)

        except requests.exceptions.ConnectionError:
            st.error("❌ Não consegui conectar no n8n. O serviço está rodando? O endpoint está certo?")
            st.info("Dica: se o Streamlit estiver em Docker, use http://n8n:5678; se estiver no host, use http://localhost:5678.")
        except requests.exceptions.ReadTimeout:
            st.error("❌ Timeout aguardando o n8n responder.")
        except Exception as e:
            st.error(f"❌ Erro ao processar o PDF: {e}")

# ==== VISUALIZAÇÃO DO CONTADOR ====
st.divider()
st.subheader("📊 Estatísticas Gerais")
col1, col2 = st.columns(2)
col1.metric("Perfilados", contador["perfilado"])
col2.metric("Não perfilados", contador["nao_perfilado"])