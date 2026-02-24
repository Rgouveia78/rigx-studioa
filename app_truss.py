import streamlit as st
from fpdf import FPDF
from datetime import datetime
import math
import os

# --- 1. CONFIGURAÇÃO DE UI E SELETOR DE TEMA ---
st.set_page_config(page_title="RigX Pro - Studio A", page_icon="🏗️", layout="centered")

# Seletor de Modo no Topo
tema = st.radio("Escolha o visual do App:", ["Claro", "Escuro"], horizontal=True)

# Definição de Cores e Logos
if tema == "Escuro":
    bg_color = "#0e1117"
    text_color = "#FFFFFF"
    card_bg = "#1e2130"
    border_color = "#3d4455"
    input_bg = "#262730"
    logo_file = "logo_white.png"  # Nome exato solicitado
    metric_color = "#00ffcc"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    card_bg = "#f8f9fa"
    border_color = "#dee2e6"
    input_bg = "#f1f3f5"
    logo_file = "logo.png"       # Nome padrão
    metric_color = "#007bff"

# Aplicação do CSS Dinâmico (Removido bloqueio do Header para evitar sumiço do botão)
st.markdown(f"""
    <style>
    /* Ocultar apenas o desnecessário, sem quebrar o app */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    
    .stApp {{ background-color: {bg_color} !important; }}
    
    /* Forçar cores de texto */
    h1, h2, h3, p, span, label, .stMarkdown {{ color: {text_color} !important; }}
    
    /* Estilização de Inputs */
    .stTextInput input, .stSelectbox div, .stNumberInput input {{
        color: {text_color} !important;
        background-color: {input_bg} !important;
    }}

    /* Estilização de Expanders */
    .streamlit-expanderHeader {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-radius: 10px !important;
    }}

    /* Estilização de Métricas */
    [data-testid="stMetric"] {{ 
        background-color: {card_bg} !important; 
        border: 1px solid {border_color} !important; 
        padding: 15px; border-radius: 12px; 
    }}
    [data-testid="stMetricValue"] {{ color: {metric_color} !important; }}

    /* BOTÃO DE DOWNLOAD - FORÇANDO VISIBILIDADE */
    .stButton button {{ 
        background: linear-gradient(90deg, #007bff 0%, #0056b3 100%) !important; 
        color: white !important; 
        font-weight: 700 !important; 
        width: 100% !important; 
        border-radius: 10px !important; 
        height: 3.5em !important;
        display: block !important;
        opacity: 1 !important;
        visibility: visible !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DADOS TÉCNICOS ---
TRUSS = {"Q15": {"k": 3200, "p": 2.6, "limit": 6}, "Q25": {"k": 12600, "p": 5.5, "limit": 10}, "Q30": {"k": 22300, "p": 7.5, "limit": 12}, "Q50": {"k": 48600, "p": 12.0, "limit": 18}}
LEDS = {"P2 Indoor": 28, "P2 Outdoor": 38, "P3 Indoor": 30, "P3 Outdoor": 40, "P5": 32, "P6": 35}
BUMPERS = {"Bumper 0.5m": 4.5, "Bumper 1.0m": 8.2}

# --- 3. HEADER DINÂMICO ---
if os.path.exists(logo_file):
    st.image(logo_file, width=150)
else:
    st.warning(f"Arquivo {logo_file} não encontrado na pasta.")
    st.title("🏗️ RigX Pro")

st.caption(f"Studio A Eventos | Modo {tema}")

# --- 4. INPUTS ---
st.subheader("📋 Dados do Job")
e_nome = st.text_input("Evento / Cliente *")
os_num = st.text_input("O.S. / Contrato *")
u_nome = st.text_input("Técnico Responsável", value="Equipe Studio A")
e_data = st.date_input("Data do Evento", format="DD/MM/YYYY")

with st.expander("🛠️ Configuração Técnica", expanded=True):
    m_truss = st.selectbox("Modelo Treliça", list(TRUSS.keys()), index=2)
    m_led = st.selectbox("Modelo LED", list(LEDS.keys()))
    larg = st.number_input("Largura LED (m)", 1.0, 30.0, 4.0, 0.5)
    alt = st.number_input("Altura LED (m)", 1.0, 15.0, 3.0, 0.5)
    t_bump = st.selectbox("Tipo Bumper", list(BUMPERS.keys()))
    q_bump = st.number_input("Qtd Bumpers", 1, 20, 4)
    vao_manual = st.number_input("Vão Nominal (m)", 1.0, 30.0, 6.0, 0.1)
    vao = st.slider("Ajuste Slider (m)", 1.0, 25.0, float(vao_manual), 0.1)

# --- 5. CÁLCULOS ---
area_led = larg * alt
peso_led = area_led * LEDS[m_led]
peso_bumps = q_bump * BUMPERS[t_bump]
total_carga = peso_led + peso_bumps
k, p_m, lim = TRUSS[m_truss]["k"], TRUSS[m_truss]["p"], TRUSS[m_truss]["limit"]
capacidade = ((k / (vao**2)) * 0.8) - (p_m * vao)
is_safe = vao <= lim and total_carga <= capacidade

# --- 6. RESULTADOS ---
st.write("---")
c1, c2 = st.columns(2)
c1.metric("Carga Total", f"{total_carga:.1f} kg")
c2.metric("Capacidade RigX", f"{capacidade:.1f} kg")

if is_safe:
    st.success("✅ ESTRUTURA APROVADA")
    status_txt = "APROVADO / SEGURO"
    recomenda = ""
else:
    st.error("🚨 ESTRUTURA REPROVADA")
    v_sug = math.sqrt((k * 0.8) / (total_carga + (p_m * vao)))
    recomenda = f"AÇÃO: Reduzir vão para {v_sug:.2f}m ou usar modelo superior."
    st.warning(recomenda)
    status_txt = "REPROVADO / RISCO"

# --- 7. FUNÇÃO PDF ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    if os.path.exists("logo.png"): pdf.image("logo.png", 10, 8, 33)
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(80); pdf.cell(110, 10, "LAUDO TECNICO ESTRUTURAL", ln=True, align='C')
    pdf.ln(12)
    pdf.set_fill_color(235, 235, 235); pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 7, " 1. IDENTIFICACAO", ln=True, fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(95, 7, f"Evento: {e_nome.upper()[:40]}", border='B'); pdf.cell(95, 7, f"O.S.: {os_num}", border='B', ln=True)
    pdf.ln(3); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, " 2. ESPECIFICACOES", ln=True, fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 7, f"Painel LED: {m_led} | Carga Total: {total_carga:.1f} kg", border='B', ln=True)
    pdf.cell(0, 7, f"Estrutura: Box Truss {m_truss} | Vão: {vao:.2f} m | Capacidade: {capacidade:.1f} kg", border='B', ln=True)
    pdf.ln(6); pdf.set_font("Arial", 'B', 12)
    if is_safe:
        pdf.set_text_color(0, 100, 0); pdf.cell(0, 12, f"STATUS: {status_txt}", border=1, ln=True, align='C')
    else:
        pdf.set_text_color(150, 0, 0); pdf.cell(0, 12, f"STATUS: {status_txt}", border=1, ln=True, align='C')
        pdf.set_font("Arial", 'I', 8); pdf.set_text_color(0,0,0); pdf.multi_cell(0, 5, recomenda.upper(), align='C')
    pdf.set_text_color(0,0,0); pdf.set_y(250); pdf.line(60, 250, 150, 250)
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, f"{u_nome.upper()}", ln=True, align='C')
    pdf.set_y(275); pdf.set_font("Arial", 'I', 7); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | Studio A Eventos", align='C', ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 8. BOTÃO DE EXPORTAÇÃO ---
st.write("---")
if e_nome and os_num:
    # Geramos o PDF antes do botão para garantir que os dados estejam prontos
    pdf_bytes = generate_pdf()
    st.download_button(
        label="📂 BAIXAR LAUDO TÉCNICO PDF",
        data=pdf_bytes,
        file_name=f"RigX_{e_nome.replace(' ', '_')}_{os_num}.pdf",
        mime="application/pdf"
    )
else:
    st.info("💡 Por favor, preencha o Nome do Evento e a O.S. para habilitar o Laudo PDF.")

st.markdown(f'<div style="text-align: center; color: {text_color}; font-size: 10px; margin-top: 30px;">© 2024 STUDIO A EVENTOS | www.studioaeventos.com.br</div>', unsafe_allow_html=True)
