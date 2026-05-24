import streamlit as st
import google.generativeai as genai
import io
import re
from docxtpl import DocxTemplate, RichText
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN
st.set_page_config(page_title="UltraVET | Informes", page_icon="logo_ultravet.png", layout="centered")

# Extraer la clave secreta directamente de la nube
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = ""

# 2. COLORES Y ESTILOS "ULTRA-VET PREMIUM" (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    div[data-testid="stVerticalBlock"] > div:has(div.stRadio), .stTextArea, .stFileUploader {
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px);
        border-radius: 20px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #007682 0%, #004e56 100%); color: white;
        border-radius: 12px; padding: 15px 30px; font-weight: 600; letter-spacing: 0.5px;
        border: none; width: 100%; transition: all 0.4s ease; box-shadow: 0 4px 15px rgba(0, 118, 130, 0.3);
    }
    div.stButton > button:first-child:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0, 118, 130, 0.4); color: #e0e0e0; }
    h1 { color: #003049; font-weight: 700 !important; letter-spacing: -1px; }
    [data-testid="stSidebar"] { background-color: #003049; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] small, [data-testid="stSidebar"] label { color: #ffffff !important; }
    /* Estilo para la tarjeta de resumen */
    .resumen-card {
        background-color: #ffffff; padding: 15px; border-left: 5px solid #007682;
        border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; color: #003049;
    }
    </style>
""", unsafe_allow_html=True)

# 3. BARRA LATERAL (Ya sin pedir contraseña)
with st.sidebar:
    try:
        st.image("logo_ultravet.png", width=220)
    except:
        st.markdown("## 🩺 ULTRA-VET")
    
    st.divider()
    st.markdown("#### 🚀 Estado del Sistema")
    if API_KEY:
        st.success("✅ Conectado a la Red Neuronal Segura")
    else:
        st.error("❌ Faltan Credenciales (Revisa Streamlit Secrets)")
    
    st.divider()
    st.markdown("<small>UltraVet © 2026<br>Diseñado por: Santiago Grefa</small>", unsafe_allow_html=True)

# 4. CUERPO PRINCIPAL
st.markdown("<h1 style='text-align: center;'>Panel de Imagenología Móvil</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #576574;'>Bienvenid@, por favor completa la información solicitada para desarrollar el informe.</p>", unsafe_allow_html=True)
st.write("---")

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

# 5. MOTOR VETERINARIO CON REGLA DE AUDIO INTELIGENTE
prompt_maestro = """
Eres un Médico Veterinario Especialista en Imagenología con años de experiencia. Tu tarea es analizar el dictado de un doctor y estructurar el reporte ecográfico perfecto. El documento final NO será revisado, la precisión debe ser INTACHABLE.

REGLAS ESTRICTAS:
1. TÉRMINOS UNIDOS: Escribe SIEMPRE de forma unida: "hipoecogénico", "peripancreática", "corticomedular", "ecotextura", "hiperecogénico", "isoecogénico", "linfadenopatía".
2. CAMPOS OBLIGATORIOS (ANTI-VACÍOS): Está ESTRICTAMENTE PROHIBIDO dejar un órgano en blanco. Si el audio NO menciona un órgano (ej. Linfonodos), DEBES copiar y pegar la frase predeterminada de abajo (ej. "No se observa linfadenopatía."). NUNCA devuelvas un campo vacío.
3. DIAGNÓSTICOS DIFERENCIALES: Si hay patologías, usa el formato "sugerente de" al final del órgano con esta regla:
   - Si hay UNA SOLA patología, NO uses números: ", sugerente de ([Diagnóstico])."
   - Si hay DOS O MÁS patologías, usa números: ", sugerente de (1. [Diagnóstico A] 2. [Diagnóstico B])."
4. FILTRO DE AUDIO EN VIVO: IGNORA pausas, muletillas ("ehh", "mmm") y autocorrecciones del doctor. Extrae únicamente el dato clínico definitivo.

[FRASES PREDETERMINADAS PARA ÓRGANOS NORMALES]
- VEJIGA: Presenta moderado contenido anecoico, sin sedimento, la pared dorsal mide [medida] mm de grosor normal.
- RINONES: Riñón izquierdo, arquitectura conservada de bordes regulares, ecogenicidad normal, diferenciación corticomedular adecuada, mide [medida] cm en eje longitudinal. Riñón derecho, arquitectura conservada de bordes regulares, ecogenicidad normal, diferenciación corticomedular adecuada, mide [medida] cm de diámetro en corte longitudinal.
- HIGADO: Tamaño conservado, ecotextura granular fina, contornos aguzados, ecogenicidad conservada. La vesícula biliar presenta contenido anecoico en moderada cantidad sin sedimento, la pared tiene grosor adecuado. Vena cava, porta y aorta de tamaño normal.
- BAZO: De arquitectura conservada, ecogenicidad adecuada, ecotextura homogénea, tamaño normal, mide [medida] cm de ancho en corte transversal a nivel del hilio esplénico.
- ESTOMAGO: Pared estomacal de grosor normal, estratificación conservada, presenta contenido alimenticio en escasa cantidad y moderada cantidad de gas, la pared mide [medida] mm en el cuerpo gástrico.
- INTESTINO: En duodeno se observa: Peristaltismo normal, patrón mucoso, pared intestinal de grosor adecuado. Yeyuno: Peristaltismo adecuado, pared intestinal de grosor adecuado, patrón mucoso. Íleon: Peristaltismo adecuado, patrón mucoso, pared intestinal de grosor normal.
- COLON: Estratificación conservada, paredes intestinales de grosor normal, la pared mide [medida] mm.
- LINFONODOS: No se observa linfadenopatía.
- PANCREAS: El parénquima es homogéneo, hipoecogénico en relación con el tejido aledaño, grosor normal, mide [medida] mm en corte transversal de la rama derecha, sin liquido libre, ni esteatitis de la grasa peripancreática.
- ADRENALES: Adrenal izquierda, ecogenicidad adecuada, arquitectura conservada, tamaño normal, mide [medida] mm en el polo caudal. Adrenal derecha, ecogenicidad adecuada, arquitectura conservada, tamaño normal, mide [medida] mm en el polo caudal.

Extrae la información y devuélvela ESTRICTAMENTE en este formato de lista:

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
[OTROS_HALLAZGOS]: [Extraer o dejar espacio]
[FECHA]: [Extraer o poner fecha actual]
"""

def extraer_datos_ia(texto_ia):
    datos = {}
    claves_mayusculas = ["CLIENTE", "NOMBRE", "EDAD", "ESPECIE", "RAZA", "SEXO", "NHC", "MEDICO", "CENTRO", "REGION"]
    claves_normales = ["VEJIGA", "RINONES", "HIGADO", "BAZO", "ESTOMAGO", "INTESTINO", "COLON", "LINFONODOS", "PANCREAS", "ADRENALES", "OTROS_HALLAZGOS", "FECHA"]
    
    for clave in claves_mayusculas:
        match = re.search(rf"\[{clave}\]: (.*)", texto_ia)
        datos[clave.lower()] = match.group(1).strip().upper() if match else ""
        
    for clave in claves_normales:
        match = re.search(rf"\[{clave}\]: (.*)", texto_ia)
        texto_encontrado = match.group(1).strip() if match else ""
        
        # --- NUEVO FRANCOTIRADOR DE NEGRITAS PERFECTO ---
        # Busca "sugerente de" y aísla SOLO los paréntesis para ponerlos en negrita
        match_sugerente = re.search(r'(sugerente de\s*)(\([^)]+\))', texto_encontrado, re.IGNORECASE)
        
        if match_sugerente:
            # Parte 1: Todo el texto hasta el paréntesis (incluye el "sugerente de ")
            parte_antes = texto_encontrado[:match_sugerente.start(2)]
            # Parte 2: Exactamente el texto dentro del paréntesis (...)
            parte_bold = match_sugerente.group(2)
            # Parte 3: Cualquier cosa después del paréntesis (un punto, etc.)
            parte_despues = texto_encontrado[match_sugerente.end(2):]
            
            rt = RichText(parte_antes)
            rt.add(parte_bold, bold=True) # AQUÍ APLICA LA NEGRILLA SOLO AL PARÉNTESIS
            if parte_despues:
                rt.add(parte_despues)
            datos[clave.lower()] = rt
        else:
            # Si por algún milagro la IA dejó vacío un órgano, el sistema inyecta un espacio 
            # para no dañar el formato del Word.
            if texto_encontrado == "":
                texto_encontrado = " "
            datos[clave.lower()] = texto_encontrado
            
    return datos

if st.button("✨ PROCESAR INFORME CLÍNICO"):
    if not API_KEY:
        st.error("❌ Falla crítica: No se detectó la API Key en Streamlit Secrets.")
    elif (opcion_ingreso == "Subir Audio 🎙️" and not audio_file) or (opcion_ingreso == "Pegar Texto 📝" and not transcripcion):
        st.warning("📂 Por favor, ingresa el audio o texto del paciente.")
    else:
        with st.spinner('🧬 Analizando datos y formateando parámetros clínicos...'):
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
                
                doc = DocxTemplate("plantilla.docx")
                doc.render(contexto_datos)
                
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                st.toast("Documento estructurado con éxito", icon="✔️")
                components.html(
                    """
                    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
                    <script>
                        var audio = new Audio('https://upload.wikimedia.org/wikipedia/commons/3/34/Sound_Effect_-_Ping_Ding.ogg');
                        audio.volume = 0.5; audio.play().catch(e => console.log("Audio silenciado"));
                        var duration = 1.5 * 1000; var end = Date.now() + duration; var colors = ['#007682', '#003049'];
                        (function frame() {
                            confetti({ particleCount: 4, angle: 60, spread: 55, origin: { x: 0, y: 1 }, colors: colors });
                            confetti({ particleCount: 4, angle: 120, spread: 55, origin: { x: 1, y: 1 }, colors: colors });
                            if (Date.now() < end) { requestAnimationFrame(frame); }
                        }());
                    </script>
                    """,
                    height=0, width=0
                )
                
                st.success("### ✅ ¡Procesamiento Completo!")
                
                # --- TARJETA DE RESUMEN ---
                nombre_paciente = contexto_datos.get('nombre', 'Desconocido')
                especie_paciente = contexto_datos.get('especie', 'No especificada')
                medico = contexto_datos.get('medico', 'No especificado')
                
                st.markdown(f"""
                <div class="resumen-card">
                    <b>🔍 Resumen Rápido de Extracción:</b><br>
                    🐾 Paciente: <b>{nombre_paciente}</b> ({especie_paciente})<br>
                    🩺 Médico: <b>{medico}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE OFICIAL (.DOCX)",
                    data=buffer,
                    file_name=f"Informe_UltraVet_{nombre_paciente}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"❌ Error de Sistema: {e}")
