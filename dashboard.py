import pandas as pd 
import datetime
import streamlit as st

# Link atualizado da logo
LOGO_URL = "https://disdigital.com.br/_next/static/media/logo-colorida.3bed5ba4.webp"

# Exibir a logo no topo
top_col1, top_col2 = st.columns([1, 4])
with top_col1:
    st.image(LOGO_URL, width=150)
with top_col2:
    st.title("Dashboard de Remessas")

# Inicializando os dados no Streamlit para persistência entre interações
if 'df' not in st.session_state:
    data = {
        'ID Remessa': [1, 2, 3],
        'ID Tarefa': ['86a6j39pd', 'a1b2c3d4e5', 'z9y8x7w6v5'],
        'Projeto': ['Projeto A', 'Projeto B', 'Projeto C'],
        'Editor': [None, None, None],
        'Status': ['Sem editor', 'Sem editor', 'Sem editor'],
        'Valor Pago (R$)': [None, None, None],
        'Data Recebimento': ['01/02/2024', '02/02/2024', '03/02/2024'],
        'Prazo': ['10/02/2024', '15/02/2024', '20/02/2024'],
        'Data Pagamento': [None, None, None]
    }
    st.session_state.df = pd.DataFrame(data)

if 'tarefas' not in st.session_state:
    st.session_state.tarefas = pd.DataFrame(columns=['ID Remessa', 'Editor Designado', 'Descrição'])

# Definindo os possíveis status
status_opcoes = ['Sem editor', 'A editar', 'Editando', 'Revisar', 'Ajustando', 'Braz', 'Fechado', 'A gravar']

st.session_state.df['Status'] = pd.Categorical(st.session_state.df['Status'], categories=status_opcoes, ordered=True)

st.session_state.df['Valor Pago (R$)'] = pd.to_numeric(st.session_state.df['Valor Pago (R$)'], errors='coerce')
st.session_state.df['Prazo'] = pd.to_datetime(st.session_state.df['Prazo'], format='%d/%m/%Y', errors='coerce')

# Exibindo o DataFrame sem modificar os IDs já existentes
st.markdown(st.session_state.df.to_html(escape=False, index=False), unsafe_allow_html=True)

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
    st.success("Remessa adicionada com sucesso!")
    st.rerun()

# Formulário para atualizar remessas
st.header("Atualizar Remessa")
id_atualizar = st.number_input("ID da Remessa para Atualizar", min_value=1, step=1)
editor_atualizar = st.text_input("Editor")
status_atualizar = st.selectbox("Status", status_opcoes)
valor_atualizar = st.number_input("Valor Pago (R$)", min_value=0.0, step=0.01)
data_pagamento_atualizar = st.date_input("Data de Pagamento").strftime('%d/%m/%Y')

if st.button("Atualizar Remessa"):
    st.session_state.df.loc[st.session_state.df['ID Remessa'] == id_atualizar, ['Editor', 'Status', 'Valor Pago (R$)', 'Data Pagamento']] = [
        editor_atualizar, status_atualizar, valor_atualizar, data_pagamento_atualizar]
    st.success("Remessa atualizada com sucesso!")
    st.rerun()

# Botão para remover remessas
st.header("Remover Remessa")
id_remover = st.number_input("ID da Remessa para Remover", min_value=1, step=1)
if st.button("Remover Remessa"):
    st.session_state.df = st.session_state.df[st.session_state.df['ID Remessa'] != id_remover]
    st.success("Remessa removida com sucesso!")
    st.rerun()

# Criando relatório de pagamentos com filtragem semanal
st.header("Relatório de Pagamentos - Última Semana")
ultima_semana = datetime.datetime.today() - datetime.timedelta(days=7)
pagamentos_semana = st.session_state.df[pd.to_datetime(st.session_state.df['Data Pagamento'], format='%d/%m/%Y', errors='coerce') >= ultima_semana]
st.dataframe(pagamentos_semana.groupby('Editor', as_index=False)['Valor Pago (R$)'].sum())