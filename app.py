import streamlit as st
import google.generativeai as genai
import io
import re
from docxtpl import DocxTemplate, RichText
import streamlit.components.v1 as components  # <-- NUEVO: Para el confeti y el sonido

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="UltraVET | Informes", page_icon="logo_ultravet.png", layout="centered")

# 2. COLORES Y ESTILOS "ULTRA-VET PREMIUM" (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    div[data-testid="stVerticalBlock"] > div:has(div.stRadio), .stTextArea, .stFileUploader {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    }
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
    h1 {
        color: #003049;
        font-weight: 700 !important;
        letter-spacing: -1px;
    }
    [data-testid="stSidebar"] {
        background-color: #003049;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] small, [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. BARRA LATERAL
with st.sidebar:
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
    st.markdown("<small>UltraVet © 2026<br>Diseñado por: Santiago Grefa</small>", unsafe_allow_html=True)

# 4. CUERPO PRINCIPAL
st.markdown("<h1 style='text-align: center;'>Panel de Imagenología Móvil</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #576574;'>Bienvenid@, por favor ingresa los datos necesarios para desarrollar el informe.</p>", unsafe_allow_html=True)
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

prompt_maestro = """
Eres un Médico Veterinario Especialista en Imagenología con años de experiencia. Tu tarea es analizar el dictado de un doctor y estructurar el reporte ecográfico perfecto. El documento final NO será revisado por un humano, por lo que la precisión y ortografía médica deben ser INTACHABLES.

REGLAS ESTRICTAS DE REDACCIÓN Y ORTOGRAFÍA MÉDICA:
1. TÉRMINOS UNIDOS: NUNCA separes prefijos médicos. Escribe SIEMPRE de forma unida: "hipoecogénico" (no hipo ecogénico), "peripancreática" (no peri pancreática), "corticomedular" (no cortico medular), "ecotextura" (no eco textura), "hiperecogénico", "isoecogénico", "linfadenopatía".
2. ÓRGANOS NORMALES (SIN ALTERACIONES): Si el dictado NO menciona problemas en un órgano, o dice que está "normal", DEBES usar ESTRICTAMENTE las frases predeterminadas que están abajo. Solo debes rellenar las medidas (mm o cm) si el doctor las dictó.
3. ÓRGANOS CON PATOLOGÍAS: Si el dictado menciona alteraciones, redacta el hallazgo usando terminología médica veterinaria avanzada y perfecta ortografía. Al final de la descripción del órgano, DEBES deducir e incluir diagnósticos diferenciales obligatoriamente en este formato: ", sugerente de (1. [Diagnóstico A] 2. [Diagnóstico B])."

*** EJEMPLO DE CÓMO DEBES PENSAR Y TRADUCIR ***
Si el audio dice: "El riñón izquierdo está mal, mide 3.4 cm, se ve difuso y tiene mineralización. El estómago está engrosado, mide 4.7 mm con líquido, parece gastritis. Vejiga normal de 1.1 mm."
TU RESPUESTA DEBE SER:
[RINONES]: Riñón izquierdo, arquitectura alterada de bordes regulares, ecogenicidad difusa, diferenciación corticomedular reducida, mide 3.4 cm en eje longitudinal... presenta focos de mineralización corticomedular, sugerente de (1. Nefropatía 2. Cambios asociados a la raza).
[ESTOMAGO]: Pared estomacal de grosor levemente aumentado, estratificación conservada, presenta contenido liquido en moderada cantidad, la pared mide 4.7 mm en el cuerpo gástrico, sugerente de (1. Gastritis leve).
[VEJIGA]: Presenta moderado contenido anecoico, sin sedimento, la pared dorsal mide 1.10 mm de grosor normal.
**********************************************

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

Extrae la información y devuélvela ESTRICTAMENTE en este formato de lista. NO añadas texto extra antes ni después de la lista:

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
        texto_encontrado = match.group(1).strip() if match else ""
        
        # --- NUEVO: FRANCOTIRADOR DE NEGRITAS ---
        indice = texto_encontrado.lower().find("sugerente de")
        
        if indice != -1:
            # Separamos el texto justo donde termina "sugerente de"
            corte = indice + len("sugerente de")
            parte_normal = texto_encontrado[:corte]
            parte_enfermedades = texto_encontrado[corte:]
            
            # Aplicamos el formato avanzado de Word
            rt = RichText(parte_normal)
            rt.add(parte_enfermedades, bold=True) # Aquí se hace la magia
            datos[clave.lower()] = rt
        else:
            # Si el órgano está sano, pasa el texto normal
            datos[clave.lower()] = texto_encontrado
            
    return datos
    
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
                
                doc = DocxTemplate("plantilla.docx")
                doc.render(contexto_datos)
                
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                st.success("### ✅ Informe Generado Correctamente")
                
                # --- NUEVO EFECTO: Confeti Sutil y Sonido ---
                st.toast("Documento estructurado con éxito", icon="✔️")
                components.html(
                    """
                    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
                    <script>
                        // Sonido de Visto/Check suave
                        var audio = new Audio('https://upload.wikimedia.org/wikipedia/commons/3/34/Sound_Effect_-_Ping_Ding.ogg');
                        audio.volume = 0.5;
                        audio.play().catch(e => console.log("Audio silenciado por el navegador"));

                        // Animación de confeti desde las esquinas inferiores
                        var duration = 1.5 * 1000;
                        var end = Date.now() + duration;
                        var colors = ['#007682', '#003049']; // Colores institucionales

                        (function frame() {
                            confetti({
                                particleCount: 4,
                                angle: 60,
                                spread: 55,
                                origin: { x: 0, y: 1 },
                                colors: colors
                            });
                            confetti({
                                particleCount: 4,
                                angle: 120,
                                spread: 55,
                                origin: { x: 1, y: 1 },
                                colors: colors
                            });
                            if (Date.now() < end) {
                                requestAnimationFrame(frame);
                            }
                        }());
                    </script>
                    """,
                    height=0, width=0
                )
                # ----------------------------------------------
                
                st.download_button(
                    label="📥 DESCARGAR REPORTE OFICIAL (.DOCX)",
                    data=buffer,
                    file_name=f"Informe_UltraVet_{contexto_datos.get('nombre', 'Paciente')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"❌ Error de Sistema: {e}")
