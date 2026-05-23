import streamlit as st
import google.generativeai as genai
import io
import re
from docxtpl import DocxTemplate

# 1. CONFIGURACIÓN DE PÁGINA (Aesthetic Mode)
st.set_page_config(
    page_title="UltraVET | Inteligencia Artificial", 
    page_icon="🩺", 
    layout="centered"
)

# 2. COLORES Y ESTILOS "ULTRA-VET PREMIUM" (CSS)
st.markdown("""
    <style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Fondo general con un degradado sutil */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Tarjetas tipo Cristal (Glassmorphism) */
    div[data-testid="stVerticalBlock"] > div:has(div.stRadio), .stTextArea, .stFileUploader {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    }

    /* Botón Principal Estilo Apple/Aesthetic */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #007682 0%, #004e56 100%);
        color: white;
        border-radius: 12px;
        padding: 15px 30px;
        font-weight: 600;
        letter-spacing: 0.5px;
        border: none;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(0, 118, 130, 0.3);
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 118, 130, 0.4);
        color: #e0e0e0;
    }

    /* Estilo para los títulos */
    h1 {
        color: #003049;
        font-weight: 700 !important;
        letter-spacing: -1px;
    }
    
    /* Personalizar el sidebar */
    [data-testid="stSidebar"] {
        background-color: #003049;
    }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] small {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. BARRA LATERAL (Sidebar Profesional)
with st.sidebar:
    # Usamos st.image con el logo que subiste a GitHub
    try:
        st.image("logo_ultravet.png", width=220)
    except:
        st.markdown("## 🩺 ULTRA-VET")
    
    st.markdown("### ⚙️ Centro de Control")
    API_KEY = st.text_input("🔑 Clave Maestra API:", type="password")
    
    st.divider()
    st.markdown("#### 🚀 Estado del Sistema")
    if API_KEY:
        st.success("Conectado a la Red Neuronal")
    else:
        st.warning("Esperando Credenciales...")
    
    st.divider()
    st.markdown("<small>Versión 2.0 - UltraVet © 2024<br>Diseño Aesthetic & Pro</small>", unsafe_allow_html=True)

# 4. CUERPO PRINCIPAL
st.markdown("<h1 style='text-align: center;'>Panel de Imagenología Móvil</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #576574;'>Automatización inteligente para informes ecográficos de alta precisión.</p>", unsafe_allow_html=True)

st.write("---")

# Selección de entrada estética
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("### 🧬 Entrada de Datos")
    opcion_ingreso = st.radio("", ["Subir Audio 🎙️", "Pegar Texto 📝"], horizontal=True)

audio_file = None
transcripcion = ""

if opcion_ingreso == "Subir Audio 🎙️":
    audio_file = st.file_uploader("Arrastra el audio aquí", type=['mp3', 'wav', 'm4a', 'ogg'])
else:
    transcripcion = st.text_area("Pega la transcripción clínica:", placeholder="Dictado del médico...", height=180)

st.write("")

# 5. LÓGICA DE PROCESAMIENTO (Mantenemos la que ya funciona)
prompt_maestro = """
Extrae la información médica del caso y devuélvela ESTRICTAMENTE en el siguiente formato de lista. 
No añadas ningún texto extra antes ni después. Si un órgano no se menciona, escribe "Arquitectura conservada sin alteraciones evidentes".

[CLIENTE]: [Extraer]
[NOMBRE]: [Extraer]
[EDAD]: [Extraer]
[ESPECIE]: [Extraer]
[RAZA]: [Extraer o dejar vacío]
[SEXO]: [Extraer]
[NHC]: [Extraer o dejar vacío]
[MEDICO]: [Extraer]
[CENTRO]: [Extraer]
[REGION]: [Extraer]
[VEJIGA]: [Hallazgos]
[RINONES]: [Hallazgos]
[HIGADO]: [Hallazgos]
[BAZO]: [Hallazgos]
[ESTOMAGO]: [Hallazgos]
[INTESTINO]: [Hallazgos]
[COLON]: [Hallazgos]
[LINFONODOS]: [Hallazgos]
[PANCREAS]: [Hallazgos]
[ADRENALES]: [Hallazgos]
[FECHA]: [Extraer o poner fecha actual]
"""

def extraer_datos_ia(texto_ia):
    datos = {}
    claves_mayusculas = ["CLIENTE", "NOMBRE", "EDAD", "ESPECIE", "RAZA", "SEXO", "NHC", "MEDICO", "CENTRO", "REGION"]
    claves_normales = ["VEJIGA", "RINONES", "HIGADO", "BAZO", "ESTOMAGO", "INTESTINO", "COLON", "LINFONODOS", "PANCREAS", "ADRENALES", "FECHA"]
    for clave in claves_mayusculas:
        match = re.search(rf"\[{clave}\]: (.*)", texto_ia)
        datos[clave.lower()] = match.group(1).strip().upper() if match else ""
    for clave in claves_normales:
        match = re.search(rf"\[{clave}\]: (.*)", texto_ia)
        datos[clave.lower()] = match.group(1).strip() if match else ""
    return datos

# Botón con efecto
if st.button("✨ PROCESAR INFORME CLÍNICO"):
    if not API_KEY:
        st.error("🔑 Error: Ingresa la API Key en el menú lateral.")
    elif (opcion_ingreso == "Subir Audio 🎙️" and not audio_file) or (opcion_ingreso == "Pegar Texto 📝" and not transcripcion):
        st.warning("📂 Por favor, ingresa el audio o texto del paciente.")
    else:
        with st.spinner('🧬 La IA está analizando los hallazgos...'):
            try:
                genai.configure(api_key=API_KEY)
                modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                modelo_elegido = modelos_disponibles[0]
                model = genai.GenerativeModel(modelo_elegido)
                
                contenido_a_enviar = [prompt_maestro]
                if opcion_ingreso == "Subir Audio 🎙️":
                    audio_blob = {"mime_type": audio_file.type, "data": audio_file.getvalue()}
                    contenido_a_enviar.extend(["ESCUCHA EL AUDIO:", audio_blob])
                else:
                    contenido_a_enviar.append(f"TEXTO:\n{transcripcion}")
                
                respuesta = model.generate_content(contenido_a_enviar)
                texto_ia = respuesta.text
                contexto_datos = extraer_datos_ia(texto_ia)
                
                # Inyección en Word
                doc = DocxTemplate("plantilla.docx")
                doc.render(contexto_datos)
                
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                # Feedback visual Premium
                st.toast("🧬 Análisis completo", icon="✅")
                st.balloons()
                
                st.success("### ✅ Informe Generado Correctamente")
                st.download_button(
                    label="📥 DESCARGAR REPORTE OFICIAL (.DOCX)",
                    data=buffer,
                    file_name=f"Informe_UltraVet_{contexto_datos.get('nombre', 'Paciente')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"❌ Error de Sistema: {e}")
