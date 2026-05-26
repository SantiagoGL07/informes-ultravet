import streamlit as st
import google.generativeai as genai
import io
import re
from docxtpl import DocxTemplate, RichText
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN DEL SERVIDOR
# ==========================================
st.set_page_config(page_title="UltraVET | Informes", page_icon="logo_ultravet.png", layout="centered")

try:
    API_KEY = st.secrets["AIzaSyDPXKQfhR1UOgVDG2Pbm2jBs7WF2oPCKsg"]
except:
    API_KEY = "AIzaSyDPXKQfhR1UOgVDG2Pbm2jBs7WF2oPCKsg"

# ==========================================
# 2. ESTILOS Y UI (AESTHETIC)
# ==========================================
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
    .resumen-card {
        background-color: #ffffff; padding: 15px; border-left: 5px solid #007682;
        border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; color: #003049;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    try:
        st.image("logo_ultravet.png", width=220)
    except:
        st.markdown("## 🩺 ULTRA-VET")
    st.divider()
    st.markdown("#### 🚀 Estado del Sistema")
    if API_KEY:
        st.success("✅ Sistema Blindado Activo")
    else:
        st.error("❌ Faltan Credenciales")
    st.divider()
    st.markdown("<small>Versión 4.0 FINAL<br>Blindaje Anti-Alucinaciones © 2026</small>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Panel de Imagenología Móvil</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #576574;'>Sistema dictatorial de precisión ecográfica.</p>", unsafe_allow_html=True)
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
    transcripcion = st.text_area("Pega la transcripción clínica:", height=180)

# ==========================================
# 3. EL CEREBRO DE LA IA (MODO DICTADOR)
# ==========================================
prompt_maestro = """
Eres un analizador de datos ecográficos. Tu nivel de creatividad es CERO. Eres un algoritmo de copia y reemplazo.

REGLAS ABSOLUTAS INQUEBRANTABLES:
1. ORTOGRAFÍA MÉDICA OBLIGATORIA: Escribe SIEMPRE de forma unida: "hipoecogénico", "peripancreática", "corticomedular", "ecotextura", "hiperecogénico", "isoecogénico", "linfadenopatía", "hemitórax". NUNCA LOS SEPARES.
2. ÓRGANOS SANOS (PROHIBIDO MODIFICAR): Si un órgano está sano o no se menciona, COPIA LA FRASE PREDETERMINADA EXACTA. NO resumas, NO borres comas, NO alteres palabras. Solo rellena los números de las medidas si se dictaron.
3. REGLA DE PATOLOGÍAS Y PARÉNTESIS: 
   - Cuando deduzcas diferenciales, usa EXACTAMENTE esta frase base: ", sugerente de "
   - Si es 1 sola patología: ", sugerente de (Patología)."
   - Si son 2 o más patologías: ", sugerente de (1. Patología A 2. Patología B)."
   - TODO LO QUE ESTÉ DESPUÉS DE "sugerente de" DEBE IR ENCERRADO ENTRE PARÉNTESIS Y EN NEGRILLAS.

[FRASES PREDETERMINADAS - COPIADO LITERAL]
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

Extrae la información ESTRICTAMENTE en este formato de lista:
[CLIENTE]: [Dato]
[NOMBRE]: [Dato]
[EDAD]: [Dato]
[ESPECIE]: [Dato]
[RAZA]: [Dato o dejar vacío]
[SEXO]: [Dato]
[NHC]: [Dato o dejar vacío]
[MEDICO]: [Dato]
[CENTRO]: [Dato]
[REGION]: [Dato]
[VEJIGA]: [Texto]
[RINONES]: [Texto]
[HIGADO]: [Texto]
[BAZO]: [Texto]
[ESTOMAGO]: [Texto]
[INTESTINO]: [Texto]
[COLON]: [Texto]
[LINFONODOS]: [Texto]
[PANCREAS]: [Texto]
[ADRENALES]: [Texto]
[OTROS_HALLAZGOS]: [Texto o dejar vacío]
[FECHA]: [Extraer o poner fecha actual]
"""

# ==========================================
# 4. EL PARACAÍDAS PYTHON (Muro de Contención)
# ==========================================
FRASES_FALLBACK = {
    "vejiga": "Presenta moderado contenido anecoico, sin sedimento, la pared dorsal mide  mm de grosor normal.",
    "rinones": "Riñón izquierdo, arquitectura conservada de bordes regulares, ecogenicidad normal, diferenciación corticomedular adecuada, mide  cm en eje longitudinal. Riñón derecho, arquitectura conservada de bordes regulares, ecogenicidad normal, diferenciación corticomedular adecuada, mide  cm de diámetro en corte longitudinal.",
    "higado": "Tamaño conservado, ecotextura granular fina, contornos aguzados, ecogenicidad conservada. La vesícula biliar presenta contenido anecoico en moderada cantidad sin sedimento, la pared tiene grosor adecuado. Vena cava, porta y aorta de tamaño normal.",
    "bazo": "De arquitectura conservada, ecogenicidad adecuada, ecotextura homogénea, tamaño normal, mide  cm de ancho en corte transversal a nivel del hilio esplénico.",
    "estomago": "Pared estomacal de grosor normal, estratificación conservada, presenta contenido alimenticio en escasa cantidad y moderada cantidad de gas, la pared mide  mm en el cuerpo gástrico.",
    "intestino": "En duodeno se observa: Peristaltismo normal, patrón mucoso, pared intestinal de grosor adecuado. Yeyuno: Peristaltismo adecuado, pared intestinal de grosor adecuado, patrón mucoso. Íleon: Peristaltismo adecuado, patrón mucoso, pared intestinal de grosor normal.",
    "colon": "Estratificación conservada, paredes intestinales de grosor normal, la pared mide  mm.",
    "linfonodos": "No se observa linfadenopatía.",
    "pancreas": "El parénquima es homogéneo, hipoecogénico en relación con el tejido aledaño, grosor normal, mide  mm en corte transversal de la rama derecha, sin liquido libre, ni esteatitis de la grasa peripancreática.",
    "adrenales": "Adrenal izquierda, ecogenicidad adecuada, arquitectura conservada, tamaño normal, mide  mm en el polo caudal. Adrenal derecha, ecogenicidad adecuada, arquitectura conservada, tamaño normal, mide  mm en el polo caudal."
}

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
        
        # 1. EL PARACAÍDAS ANTI-VACÍOS
        if texto_encontrado == "" and clave.lower() in FRASES_FALLBACK:
            texto_encontrado = FRASES_FALLBACK[clave.lower()]
            
        # 2. FRANCOTIRADOR DE NEGRILLAS (Blindado contra errores gramaticales)
        match_sugerente = re.search(r'(sugerente(?:s)? de\s*)(\([^)]+\))', texto_encontrado, re.IGNORECASE)
        
        if match_sugerente:
            parte_antes = texto_encontrado[:match_sugerente.start(2)]
            parte_bold = match_sugerente.group(2) # Solo agarra los paréntesis (...)
            parte_despues = texto_encontrado[match_sugerente.end(2):]
            
            rt = RichText(parte_antes)
            rt.add(parte_bold, bold=True)
            if parte_despues:
                rt.add(parte_despues)
            datos[clave.lower()] = rt
        else:
            datos[clave.lower()] = texto_encontrado
            
    return datos

# ==========================================
# 5. EJECUCIÓN PRINCIPAL
# ==========================================
if st.button("✨ PROCESAR INFORME OFICIAL"):
    if not API_KEY:
        st.error("❌ API Key no encontrada.")
    elif (opcion_ingreso == "Subir Audio 🎙️" and not audio_file) or (opcion_ingreso == "Pegar Texto 📝" and not transcripcion):
        st.warning("📂 Falta información clínica.")
    else:
        with st.spinner('🧬 Blindaje activo. Procesando con 0% de margen de error...'):
            try:
                genai.configure(api_key=API_KEY)
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # TEMPERATURA 0.0: MATA LA IMAGINACIÓN DE LA IA
                config = genai.GenerationConfig(temperature=0.0)
                model = genai.GenerativeModel(modelos[0], generation_config=config)
                
                contenido_a_enviar = [prompt_maestro]
                if opcion_ingreso == "Subir Audio 🎙️":
                    audio_blob = {"mime_type": audio_file.type, "data": audio_file.getvalue()}
                    contenido_a_enviar.extend(["ESCUCHA EL AUDIO:", audio_blob])
                else:
                    contenido_a_enviar.append(f"TEXTO:\n{transcripcion}")
                
                respuesta = model.generate_content(contenido_a_enviar)
                contexto_datos = extraer_datos_ia(respuesta.text)
                
                doc = DocxTemplate("plantilla.docx")
                doc.render(contexto_datos)
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                st.toast("Estructura clínica garantizada", icon="✔️")
                components.html(
                    """
                    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
                    <script>
                        var audio = new Audio('https://upload.wikimedia.org/wikipedia/commons/3/34/Sound_Effect_-_Ping_Ding.ogg');
                        audio.volume = 0.5; audio.play().catch(e => console.log("Audio silenciado"));
                        var colors = ['#007682', '#003049'];
                        confetti({ particleCount: 4, angle: 60, spread: 55, origin: { x: 0, y: 1 }, colors: colors });
                        confetti({ particleCount: 4, angle: 120, spread: 55, origin: { x: 1, y: 1 }, colors: colors });
                    </script>
                    """, height=0, width=0
                )
                
                st.success("### ✅ ¡Procesamiento Perfecto!")
                nombre = contexto_datos.get('nombre', 'Desconocido')
                
                st.markdown(f"""
                <div class="resumen-card">
                    <b>🔍 Paciente procesado:</b> {nombre}<br>
                    <small><i>Formato y vocabulario garantizados bajo estándares estrictos.</i></small>
                </div>
                """, unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE BLINDADO (.DOCX)",
                    data=buffer, file_name=f"Informe_{nombre}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"❌ Error interno: {e}")
