import streamlit as st
from fpdf import FPDF
from datetime import datetime
import math
import os

# --- 1. CONFIGURAÇÃO DE UI E SELETOR DE TEMA ---
st.set_page_config(page_title="RigX Pro - Studio A", page_icon="🏗️", layout="centered")

tema = st.radio("Visual do App:", ["Claro", "Escuro"], horizontal=True)

if tema == "Escuro":
    bg_color, text_color, card_bg = "#0e1117", "#FFFFFF", "#1e2130"
    border_color, input_bg, metric_color = "#3d4455", "#262730", "#00ffcc"
    logo_file = "logo_white.png"
else:
    bg_color, text_color, card_bg = "#FFFFFF", "#000000", "#f8f9fa"
    border_color, input_bg, metric_color = "#dee2e6", "#f1f3f5", "#007bff"
    logo_file = "logo.png"

st.markdown(f"""
    <style>
    #MainMenu, footer {{ visibility: hidden; }}
    .stApp {{ background-color: {bg_color} !important; }}
    h1, h2, h3, p, span, label, .stMarkdown {{ color: {text_color} !important; }}
    .stTextInput input, .stSelectbox div, .stNumberInput input {{ color: {text_color} !important; background-color: {input_bg} !important; }}
    .streamlit-expanderHeader {{ background-color: {card_bg} !important; color: {text_color} !important; border-radius: 10px !important; }}
    [data-testid="stMetric"] {{ background-color: {card_bg} !important; border: 1px solid {border_color} !important; padding: 15px; border-radius: 12px; }}
    [data-testid="stMetricValue"] {{ color: {metric_color} !important; }}
    .stButton button {{ 
        background: linear-gradient(90deg, #007bff 0%, #0056b3 100%) !important; 
        color: white !important; font-weight: 700 !important; width: 100% !important; 
        border-radius: 10px !important; height: 3.5em !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
TRUSS = {"Q15": {"k": 3200, "p": 2.6, "limit": 6}, "Q25": {"k": 12600, "p": 5.5, "limit": 10}, "Q30": {"k": 22300, "p": 7.5, "limit": 12}, "Q50": {"k": 48600, "p": 12.0, "limit": 18}}
LEDS = {"P2 Indoor": 28, "P2 Outdoor": 38, "P3 Indoor": 30, "P3 Outdoor": 40, "P5": 32, "P6": 35}
BUMPERS = {"Bumper 0.5m": 4.5, "Bumper 1.0m": 8.2}

# --- 3. HEADER COM LOGO ---
if os.path.exists(logo_file):
    st.image(logo_file, width=150)
else:
    st.title("🏗️ RigX Pro")
    st.caption(f"Aviso: Arquivo {logo_file} não encontrado na pasta.")

# --- 4. INPUTS DO USUÁRIO ---
st.subheader("📋 Detalhes do Projeto")
e_nome = st.text_input("Evento / Cliente *")
os_num = st.text_input("O.S. / Contrato *")
u_nome = st.text_input("Técnico Responsável", value="Equipe Studio A")
e_data = st.date_input("Data do Evento", format="DD/MM/YYYY")

with st.expander("🛠️ Configuração Técnica", expanded=True):
    m_truss = st.selectbox("Modelo Treliça", list(TRUSS.keys()), index=2)
    m_led = st.selectbox("Modelo LED", list(LEDS.keys()))
    larg = st.number_input("Largura LED (m)", value=4.0, step=0.5)
    alt = st.number_input("Altura LED (m)", value=3.0, step=0.5)
    t_bump = st.selectbox("Tipo Bumper", list(BUMPERS.keys()))
    q_bump = st.number_input("Qtd Bumpers", min_value=1, value=4)
    vao_manual = st.number_input("Vão Nominal (m)", value=6.0, step=0.1)
    vao = st.slider("Ajuste do Vão (m)", 1.0, 25.0, float(vao_manual), 0.1)

# --- 5. CÁLCULOS ---
area_led = larg * alt
peso_led_total = area_led * LEDS[m_led]
peso_bumps_total = q_bump * BUMPERS[t_bump]
total_carga = peso_led_total + peso_bumps_total
k, p_m, lim = TRUSS[m_truss]["k"], TRUSS[m_truss]["p"], TRUSS[m_truss]["limit"]
capacidade = ((k / (vao**2)) * 0.8) - (p_m * vao)
is_safe = vao <= lim and total_carga <= capacidade

# --- 6. RESULTADOS ---
st.write("---")
c1, c2 = st.columns(2)
c1.metric("Carga Total", f"{total_carga:.1f} kg")
c2.metric("Capacidade RigX", f"{capacidade:.1f} kg")

status_txt = "APROVADO / SEGURO" if is_safe else "REPROVADO / RISCO"
recomenda = ""
if not is_safe:
    v_sug = math.sqrt((k * 0.8) / (total_carga + (p_m * vao)))
    recomenda = f"Reduzir vao para {v_sug:.2f}m ou usar modelo superior."
    st.error(f"🚨 ESTRUTURA REPROVADA. {recomenda}")
else:
    st.success("✅ ESTRUTURA APROVADA")

# --- 7. GERADOR DE PDF PROFISSIONAL (PÁGINA ÚNICA) ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    if os.path.exists("logo.png"): pdf.image("logo.png", 10, 8, 33)
    
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(80); pdf.cell(110, 10, "LAUDO TECNICO ESTRUTURAL", ln=True, align='C')
    pdf.set_font("Arial", '', 9); pdf.cell(80); pdf.cell(110, 5, "SISTEMA RIGX PRO - STUDIO A EVENTOS", ln=True, align='C')
    pdf.ln(12)

    # Bloco 1: Identificação
    pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, " 1. IDENTIFICACAO DO PROJETO", ln=True, fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(95, 7, f"Evento: {e_nome.upper()[:40]}", border='B'); pdf.cell(95, 7, f"O.S.: {os_num}", border='B', ln=True)
    pdf.cell(95, 7, f"Tecnico: {u_nome}", border='B'); pdf.cell(95, 7, f"Data: {e_data.strftime('%d/%m/%Y')}", border='B', ln=True)
    
    # Bloco 2: Detalhamento Carga (ATUALIZADO COM MEDIDAS)
    pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, " 2. ESPECIFICACAO DA CARGA", ln=True, fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(95, 7, f"Modelo LED: {m_led}", border='B'); pdf.cell(95, 7, f"Dimensao: {larg}m (L) x {alt}m (A)", border='B', ln=True)
    pdf.cell(95, 7, f"Area Total: {area_led:.2f} m2", border='B'); pdf.cell(95, 7, f"Peso LED (Liquido): {peso_led_total:.1f} kg", border='B', ln=True)
    pdf.cell(95, 7, f"Içamento: {q_bump}x {t_bump}", border='B'); pdf.cell(95, 7, f"Peso Bumpers: {peso_bumps_total:.1f} kg", border='B', ln=True)
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 10, f"PESO TOTAL DA CARGA (LED + ACESSORIOS): {total_carga:.1f} kg", ln=True)

    # Bloco 3: Estrutura
    pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, " 3. DIMENSIONAMENTO DA ESTRUTURA", ln=True, fill=True)
    pdf.set_font("Arial", '', 9)
    pdf.cell(95, 7, f"Modelo Trelica: Box Truss {m_truss}", border='B'); pdf.cell(95, 7, f"Vao Calculado: {vao:.2f} m", border='B', ln=True)
    pdf.cell(0, 7, f"Capacidade de Carga Segura p/ este Vao: {capacidade:.1f} kg", border='B', ln=True)

    # Bloco 4: Veredito
    pdf.ln(8); pdf.set_font("Arial", 'B', 12)
    if is_safe:
        pdf.set_text_color(0, 100, 0); pdf.set_fill_color(210, 255, 210)
        pdf.cell(0, 12, f" STATUS FINAL: {status_txt}", border=1, ln=True, align='C', fill=True)
    else:
        pdf.set_text_color(150, 0, 0); pdf.set_fill_color(255, 210, 210)
        pdf.cell(0, 12, f" STATUS FINAL: {status_txt}", border=1, ln=True, align='C', fill=True)
        pdf.set_font("Arial", 'B', 9); pdf.ln(2); pdf.set_text_color(0,0,0)
        pdf.multi_cell(0, 6, f"RECOMENDACAO: {recomenda.upper()}", align='C')

    # Bloco 5: Assinatura
    pdf.set_text_color(0,0,0); pdf.set_y(250); pdf.line(60, 250, 150, 250)
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 7, f"{u_nome.upper()}", ln=True, align='C')
    pdf.set_y(275); pdf.set_font("Arial", 'I', 7); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | Studio A Eventos", align='C', ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 8. BOTÃO DE EXPORTAÇÃO ---
st.write("---")
if e_nome and os_num:
    st.download_button(label="📂 GERAR LAUDO TÉCNICO COMPLETO", data=generate_pdf(), file_name=f"Laudo_RigX_{e_nome.replace(' ', '_')}_OS_{os_num}.pdf", mime="application/pdf")
else:
    st.info("💡 Por favor, preencha o Nome do Evento e a O.S. para habilitar o Laudo PDF.")

st.markdown(f'<div style="text-align: center; color: {text_color}; font-size: 10px; margin-top: 30px;">© 2024 STUDIO A EVENTOS | www.studioaeventos.com.br</div>', unsafe_allow_html=True)
