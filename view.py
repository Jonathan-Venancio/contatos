import streamlit as st
import pandas as pd
import os

# Criar pasta de uploads se não existir
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="Visualizador de Clínicas", layout="centered")

# Upload na sidebar
with st.sidebar:
    st.title("📂 Painel de Controle")
    
    # Buscar todos os .xlsx (do diretório principal + uploads)
    arquivos_planilha = [
        os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR) if f.endswith(".xlsx")
    ] + [
        f for f in os.listdir() if f.endswith(".xlsx") and not f.startswith("~$")
    ]

    if not arquivos_planilha:
        st.error("Nenhuma planilha .xlsx encontrada.")
        st.stop()

    nomes_amigaveis = [os.path.splitext(os.path.basename(f))[0] for f in arquivos_planilha]
    nome_escolhido = st.selectbox("🌆 Selecione a Cidade:", nomes_amigaveis)

    st.markdown("---")
    st.subheader("🔀 Modo de Navegação")
    modo = st.radio("Como deseja visualizar?", ["Próxima automaticamente", "Selecionar manualmente"])

    st.markdown("---")
     # Upload de Excel
    arquivos_enviados = st.file_uploader("📤 Enviar planilha (.xlsx)", type="xlsx", accept_multiple_files=True)
    if arquivos_enviados:
        for arquivo in arquivos_enviados:
            caminho_salvo = os.path.join(UPLOAD_DIR, arquivo.name)
            with open(caminho_salvo, "wb") as f:
                f.write(arquivo.read())
        st.success(f"{len(arquivos_enviados)} arquivo(s) enviado(s) com sucesso!")

# Mapear nome amigável para caminho do arquivo
arquivo_selecionado = arquivos_planilha[nomes_amigaveis.index(nome_escolhido)]
titulo = os.path.splitext(os.path.basename(arquivo_selecionado))[0]
st.title(f"📋 Visualizador de Clínicas: {titulo}")

# Ler o Excel
try:
    xls = pd.ExcelFile(arquivo_selecionado)
    df = pd.read_excel(xls, sheet_name='Recuperada_Planilha1')
except Exception as e:
    st.error(f"Erro ao carregar a planilha: {e}")
    st.stop()

# Garantir coluna 'contactado'
if 'contactado' not in df.columns:
    df['contactado'] = 'não'

# Estatísticas
total = len(df)
ja_contactadas = (df['contactado'].str.lower() == 'sim').sum()
nao_contactadas = total - ja_contactadas
st.info(f"📊 Total: **{total}** | ✅ Contactadas: **{ja_contactadas}** | 🔔 Faltando: **{nao_contactadas}**")

# Sessão
if 'indice_atual' not in st.session_state:
    st.session_state.indice_atual = 0
if 'modo_manual' not in st.session_state:
    st.session_state.modo_manual = False

# Filtros
df_nao_contactadas = df[df['contactado'].str.lower() == 'não']
df_contactadas = df[df['contactado'].str.lower() == 'sim']

# Selecionar clínica
if modo == "Selecionar manualmente":
    st.session_state.modo_manual = True
    nomes = df['Nome clinica'].dropna().unique()
    nome_selecionado = st.selectbox("Escolha a clínica:", nomes)
    clinica_atual = df[df['Nome clinica'] == nome_selecionado].iloc[0]
else:
    st.session_state.modo_manual = False
    if df_nao_contactadas.empty:
        st.success("🎉 Todas as clínicas foram contactadas!")
        st.stop()
    clinica_atual = df_nao_contactadas.iloc[st.session_state.indice_atual]
    nome_selecionado = clinica_atual['Nome clinica']

# Exibir dados
col1, col2 = st.columns(2)
with col1:
    st.subheader("📌 Detalhes da Clínica")
    st.markdown(f"**Nome da Clínica:** {clinica_atual['Nome clinica']}")
    st.markdown(f"**Especialidade:** {clinica_atual['Especialidade']}")
    st.markdown(f"**Avaliação no Google:** {clinica_atual['avaliação no google']}")
    st.markdown(f"**Endereço:** {clinica_atual['Endereço']}")
    st.markdown(f"**Telefone:** {clinica_atual['Telefone']}")

with col2:
    st.subheader("🔗 Links")
    maps_link = clinica_atual['link maps']
    if pd.notna(maps_link) and str(maps_link).startswith("http"):
        st.link_button("📍 Google Maps", maps_link)

    site_link = clinica_atual['Website']
    if pd.notna(site_link) and str(site_link).startswith("http"):
        st.link_button("🌐 Website", site_link)
    
    if st.button("✅ Marcar como contactada"):
        idx_real = df[df['Nome clinica'] == nome_selecionado].index[0]
        df.at[idx_real, 'contactado'] = 'sim'
        df.to_excel(arquivo_selecionado, sheet_name='Recuperada_Planilha1', index=False)
        st.success("Clínica marcada como contactada.")
        st.rerun()
    
    if not st.session_state.modo_manual and st.button("➡️ Próxima não contactada"):
        st.session_state.indice_atual += 1
        if st.session_state.indice_atual >= len(df_nao_contactadas):
            st.session_state.indice_atual = 0
        st.rerun()

#Qualificação de cliente
st.subheader("📄 Qualificação")

st.text_input('Vocês utilizam agendamentos via WhatsApp atualmente? (Se sim, verificar como é feito e os desafios enfrentados.)')
st.text_input('Quantas consultas são agendadas por mês na clínica? (Ajuda a entender a demanda.)')
st.text_input('A equipe sente dificuldades com marcações e confirmações de consulta? (Identifica dor do cliente.)')
st.text_input('Vocês já pensaram em automatizar esse processo para reduzir tempo de atendimento e erros? (Gera reflexão e interesse.)')
st.text_input('Qual ferramenta ou sistema utilizam atualmente para gerenciar os agendamentos? (Facilita integração com soluções.)')

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("✅ Qualificado"):
        idx_real2 = df[df['Nome clinica'] == nome_selecionado].index[0]
        df.at[idx_real2, 'contactado'] = 'sim'
        df.to_excel(arquivo_selecionado, sheet_name='Recuperada_Planilha1', index=False)
        st.success("Clínica marcada como contactada.")
        st.rerun()

with col2:
    if st.button("🚫 Desqualificado"):
        st.rerun()

with col3:
    if st.button("⌛ Futuro Cliente"):
        st.rerun()

with col4:  
    if st.button("❌ Excluir"):
        idx_real = df[df['Nome clinica'] == nome_selecionado].index[0]
        df = df.drop(idx_real).reset_index(drop=True)
        df.to_excel(arquivo_selecionado, sheet_name='Recuperada_Planilha1', index=False)
        st.warning("Clínica excluída da planilha.")
        st.rerun()

# Tabelas
st.markdown("---")
st.subheader("📋 Clínicas NÃO contactadas")
st.dataframe(df_nao_contactadas[['Nome clinica', 'Especialidade', 'Telefone']], use_container_width=True)

st.subheader("📋 Clínicas JÁ contactadas")
st.dataframe(df_contactadas[['Nome clinica', 'Especialidade', 'Telefone']], use_container_width=True)
