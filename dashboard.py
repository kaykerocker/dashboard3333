import pandas as pd
import datetime
import streamlit as st
import gspread
import json
import os
from google.oauth2.service_account import Credentials

# Configuração do Google Sheets
SHEET_ID = "1SiV6SmYfYXGG1cwXXbDESOSK6lB4_JyPKXBM70s3KiE"
SHEET_NAME = "Remessas"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Verificar se estamos rodando localmente ou no Streamlit Cloud
if os.path.exists("credenciais.json"):  # Se o arquivo local existir, use ele
    credentials = Credentials.from_service_account_file("credenciais.json", scopes=SCOPES)
    st.write("✅ Usando credenciais locais (credenciais.json)")
elif "GOOGLE_CREDENTIALS" in os.environ:  # Se a variável de ambiente existir, use ela
    try:
        st.write("✅ Variável GOOGLE_CREDENTIALS encontrada! Iniciando autenticação...")
        service_account_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
        credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        st.write("✅ Autenticação bem-sucedida!")
    except Exception as e:
        st.error(f"❌ Erro ao carregar GOOGLE_CREDENTIALS: {str(e)}")
        st.stop()
else:
    st.error("❌ Nenhuma credencial do Google encontrada. Configure 'GOOGLE_CREDENTIALS' no GitHub ou adicione 'credenciais.json' localmente.")
    st.stop()


client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

def load_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_data(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Carregar dados da planilha Google
st.session_state.df = load_data()

# Link atualizado da logo
LOGO_URL = "https://disdigital.com.br/_next/static/media/logo-colorida.3bed5ba4.webp"

# Exibir a logo no topo
top_col1, top_col2 = st.columns([1, 4])
with top_col1:
    st.image(LOGO_URL, width=150)
with top_col2:
    st.title("Dashboard de Remessas")

# Exibindo o DataFrame
st.dataframe(st.session_state.df, width=1200, height=600)

# Formulário para adicionar novas remessas
st.header("Adicionar Nova Remessa")
id_remessa = st.number_input("ID Remessa", min_value=1, step=1)
id_tarefa = st.text_input("ID da Tarefa (ClickUp)")
projeto = st.text_input("Projeto")
data_recebimento = st.date_input("Data de Recebimento").strftime('%d/%m/%Y')
prazo = st.date_input("Prazo").strftime('%d/%m/%Y')

if st.button("Adicionar Remessa"):
    novo_id_tarefa = f'<a href="https://app.clickup.com/t/{id_tarefa}" target="_blank">{id_tarefa}</a>' if id_tarefa else ''
    nova_remessa = pd.DataFrame([{
        'ID Remessa': id_remessa,
        'ID Tarefa': novo_id_tarefa,
        'Projeto': projeto,
        'Editor': None,
        'Status': 'Sem editor',
        'Valor Pago (R$)': None,
        'Data Recebimento': data_recebimento,
        'Prazo': prazo,
        'Data Pagamento': None
    }])
    st.session_state.df = pd.concat([st.session_state.df, nova_remessa], ignore_index=True)
    save_data(st.session_state.df)
    st.success("Remessa adicionada com sucesso!")
    st.rerun()

# Formulário para atualizar remessas
st.header("Atualizar Remessa")
id_atualizar = st.number_input("ID da Remessa para Atualizar", min_value=1, step=1)
editor_atualizar = st.text_input("Editor")
status_atualizar = st.selectbox("Status", st.session_state.df['Status'].unique())
valor_atualizar = st.number_input("Valor Pago (R$)", min_value=0.0, step=0.01)
data_pagamento_atualizar = st.date_input("Data de Pagamento").strftime('%d/%m/%Y')

if st.button("Atualizar Remessa"):
    st.session_state.df.loc[st.session_state.df['ID Remessa'] == id_atualizar, ['Editor', 'Status', 'Valor Pago (R$)', 'Data Pagamento']] = [
        editor_atualizar, status_atualizar, valor_atualizar, data_pagamento_atualizar]
    save_data(st.session_state.df)
    st.success("Remessa atualizada com sucesso!")
    st.rerun()

# Botão para remover remessas
st.header("Remover Remessa")
id_remover = st.number_input("ID da Remessa para Remover", min_value=1, step=1)
if st.button("Remover Remessa"):
    st.session_state.df = st.session_state.df[st.session_state.df['ID Remessa'] != id_remover]
    save_data(st.session_state.df)
    st.success("Remessa removida com sucesso!")
    st.rerun()

# Criando relatório de pagamentos com filtragem semanal
st.header("Relatório de Pagamentos - Última Semana")
ultima_semana = datetime.datetime.today() - datetime.timedelta(days=7)
pagamentos_semana = st.session_state.df[pd.to_datetime(st.session_state.df['Data Pagamento'], format='%d/%m/%Y', errors='coerce') >= ultima_semana]
st.dataframe(pagamentos_semana.groupby('Editor', as_index=False)['Valor Pago (R$)'].sum())
