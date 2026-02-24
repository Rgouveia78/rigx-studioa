import streamlit as st
from fpdf import FPDF
from datetime import datetime
import math
import os

# --- 1. CONFIGURAÇÃO DE UI/UX ---
st.set_page_config(page_title="RigX Pro - Studio A", page_icon="🏗️", layout="centered")

# CSS Avançado: Glassmorphism e Cores Semânticas
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0e1117; }
    .stMetric { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; }
    .status-card { padding: 20px; border-radius: 15px; text-align: center; font-weight: 600; margin-bottom: 20px; }
    .safe { background-color: rgba(0, 255, 153, 0.1); border: 1px solid #00ff99; color: #00ff99; }
    .danger { background-color: rgba(255, 75, 75, 0.1); border: 1px solid #ff4b4b; color: #ff4b4b; }
    .stButton>button { border-radius: 12px; height: 3.5em; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .footer { text-align: center; color: #666; font-size: 11px; margin-top: 50px; padding: 20px; border-top: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE DADOS ---
TRUSS = {
    "Q15": {"k": 3200, "p": 2.6, "limit": 6},
    "Q25": {"k": 12600, "p": 5.5, "limit": 10},
    "Q30": {"k": 22300, "p": 7.5, "limit": 12},
    "Q50": {"k": 48600, "p": 12.0, "limit": 18}
}
LEDS = {"P2 Indoor": 28, "P2 Outdoor": 38, "P3 Indoor": 30, "P3 Outdoor": 40, "P5": 32, "P6": 35}
BUMPERS = {"Bumper 0.5m": 4.5, "Bumper 1.0m": 8.2}

# --- 3. HEADER INTELIGENTE ---
def load_logo():
    if os.path.exists("logo_white.png"):
        st.image("logo_white.png", width=140)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=140)
    else:
        st.title("🏗️ RigX Pro")

load_logo()
st.caption("Studio A Eventos | Engenharia Estrutural de Precisão")

# --- 4. FORMULÁRIO DE ENTRADA ---
with st.container():
    st.subheader("📋 Informações do Projeto")
    c1, c2 = st.columns(2)
    e_nome = c1.text_input("Evento / Cliente *", placeholder="Nome do Job")
    os_num = c2.text_input("O.S. / Contrato *", placeholder="Código da O.S.")
    
    c3, c4 = st.columns(2)
    u_nome = c3.text_input("Responsável Técnico", value="Equipe Studio A")
    e_data = c4.date_input("Data do Evento", format="DD/MM/YYYY")

with st.expander("🛠️ Configuração de Hardware", expanded=True):
    col1, col2 = st.columns(2)
    m_truss = col1.selectbox("Treliça Box Truss", list(TRUSS.keys()), index=2)
    m_led = col2.selectbox("Modelo do LED", list(LEDS.keys()))
    
    col3, col4, col5 = st.columns(3)
    larg = col3.number_input("Largura (m)", 1.0, 30.0, 4.0, 0.5)
    alt = col4.number_input("Altura (m)", 1.0, 15.0, 3.0, 0.5)
    peso_led_manual = col5.number_input("Peso LED (kg/m²)", 10, 80, LEDS[m_led])
    
    col6, col7 = st.columns(2)
    t_bump = col6.selectbox("Acessório Bumper", list(BUMPERS.keys()))
    q_bump = col7.number_input("Qtd Bumpers", 1, 20, 4)

with st.expander("📐 Dimensionamento do Vão", expanded=True):
    vao_manual = st.number_input("Vão Nominal (m)", 1.0, 30.0, 6.0, 0.1)
    vao = st.slider("Ajuste de Precisão", 1.0, 25.0, float(vao_manual), 0.1)

# --- 5. CÁLCULOS E LÓGICA ---
peso_led = (larg * alt) * peso_led_manual
peso_bumps = q_bump * BUMPERS[t_bump]
total_carga = peso_led + peso_bumps

k, p_m, lim = TRUSS[m_truss]["k"], TRUSS[m_truss]["p"], TRUSS[m_truss]["limit"]
# Fórmula de Rigidez com Coeficiente de Segurança 1.25 (80% da capacidade)
capacidade = ((k / (vao**2)) * 0.8) - (p_m * vao)

# --- 6. DISPLAY DE RESULTADOS ---
st.write("---")
res1, res2 = st.columns(2)
res1.metric("Carga Solicitada", f"{total_carga:.1f} kg")
res2.metric("Capacidade Segura", f"{capacidade:.1f} kg")

is_safe = vao <= lim and total_carga <= capacidade

if is_safe:
    st.markdown(f'<div class="status-card safe">✅ ESTRUTURA APROVADA PARA MONTAGEM</div>', unsafe_allow_html=True)
    recomenda = ""
else:
    st.markdown(f'<div class="status-card danger">🚨 ESTRUTURA REPROVADA - RISCO DETECTADO</div>', unsafe_allow_html=True)
    vao_max = math.sqrt((k * 0.8) / (total_carga + (p_m * vao)))
    recomenda = f"AÇÃO CORRETIVA: Reduzir vão para {vao_max:.2f}m ou migrar para modelo superior."
    st.warning(recomenda)

# --- 7. GERADOR DE RELATÓRIO PDF ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Header Logo
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 30)
    
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(0, 10, "RELATÓRIO TÉCNICO DE CARGA - RigX Pro", ln=True, align='R')
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, f"Studio A Eventos | OS: {os_num}", ln=True, align='R')
    pdf.cell(0, 5, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='R')
    
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, f" EVENTO: {e_nome.upper()}", ln=True, fill=True)
    
    pdf.set_font("Arial", '', 11)
    pdf.ln(5)
    items = [
        ("Técnico Responsável", u_nome),
        ("Modelo de Treliça", f"Box Truss {m_truss}"),
        ("Vão Calculado", f"{vao:.2f} metros"),
        ("Painel de LED", f"{m_led} ({larg}x{alt}m)"),
        ("Peso Bumpers", f"{peso_bumps:.1f} kg ({q_bump}x {t_bump})"),
        ("PESO TOTAL DA CARGA", f"{total_carga:.1f} kg"),
        ("CAPACIDADE DO MODELO", f"{capacidade:.1f} kg")
    ]
    for label, value in items:
        pdf.set_font("Arial", 'B', 10); pdf.cell(50, 8, label + ":", 0)
        pdf.set_font("Arial", '', 10); pdf.cell(0, 8, value, ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    if is_safe:
        pdf.set_text_color(0, 153, 76)
        pdf.cell(0, 12, "STATUS: APROVADO / SEGURO", border=1, ln=True, align='C')
    else:
        pdf.set_text_color(204, 0, 0)
        pdf.cell(0, 12, "STATUS: REPROVADO / RISCO", border=1, ln=True, align='C')
        pdf.set_font("Arial", 'I', 10); pdf.ln(2); pdf.cell(0, 10, recomenda, ln=True, align='C')

    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 8); pdf.cell(0, 5, "AVISO DE RESPONSABILIDADE:", ln=True)
    pdf.set_font("Arial", '', 7)
    pdf.multi_cell(0, 4, "Este relatório é uma estimativa baseada em parâmetros técnicos de fabricantes de alumínio liga 6082-T6. A montagem deve ser supervisionada por profissional habilitado (ART). A Studio A Eventos não se responsabiliza por montagens em desacordo com as normas NBR 16031 ou erros de operação em campo.")
    
    return pdf.output(dest='S').encode('latin-1')

# --- 8. FINALIZAÇÃO ---
st.write("---")
if e_nome and os_num:
    pdf_data = generate_pdf()
    st.download_button(
        label="📂 EXPORTAR LAUDO OFICIAL (PDF)",
        data=pdf_data,
        file_name=f"RigX_{e_nome.replace(' ', '_')}_{os_num}.pdf",
        mime="application/pdf"
    )
else:
    st.info("💡 Complete o Nome do Evento e O.S. para gerar o Laudo.")

st.markdown('<div class="footer">© 2024 STUDIO A EVENTOS | www.studioaeventos.com.br<br>Cálculos baseados em normas ABNT de segurança estrutural.</div>', unsafe_allow_html=True)
