import streamlit as st
import google.generativeai as genai
import io
import re
from docxtpl import DocxTemplate

st.set_page_config(page_title="Informes Ecográficos UltraVet", layout="centered")
st.title("🩺 Informes UltraVET")
st.write("Bienvenid@, por favor sube el audio del informe o pega la transcripción para generar el documento de UltraVet.")

API_KEY = st.text_input("Ingresa tu API Key de Gemini:", type="password")

# --- NUEVO: Selección de método de ingreso ---
st.subheader("1. Ingresa la información médica")
opcion_ingreso = st.radio("¿Cómo prefieres ingresar los datos?", ["Subir Audio 🎙️", "Pegar Texto 📝"])

audio_file = None
transcripcion = ""

if opcion_ingreso == "Subir Audio 🎙️":
    audio_file = st.file_uploader("Sube la grabación (MP3, WAV, M4A, OGG)", type=['mp3', 'wav', 'm4a', 'ogg'])
else:
    transcripcion = st.text_area("📝 Pega aquí el texto:", height=200)

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

if st.button("Generar Informe UltraVet"):
    if not API_KEY:
        st.warning("⚠️ Asegúrate de poner la API Key.")
    elif opcion_ingreso == "Subir Audio 🎙️" and not audio_file:
        st.warning("⚠️ Por favor sube un archivo de audio.")
    elif opcion_ingreso == "Pegar Texto 📝" and not transcripcion:
        st.warning("⚠️ Por favor pega el texto del caso.")
    else:
        with st.spinner('Escuchando, analizando y acoplando a la plantilla...'):
            try:
                genai.configure(api_key=API_KEY)
                modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                modelo_elegido = modelos_disponibles[0]
                model = genai.GenerativeModel(modelo_elegido)
                
                # --- NUEVO: Empaquetar audio o texto para la IA ---
                contenido_a_enviar = [prompt_maestro]
                
                if opcion_ingreso == "Subir Audio 🎙️":
                    audio_blob = {
                        "mime_type": audio_file.type,
                        "data": audio_file.getvalue()
                    }
                    contenido_a_enviar.append("ESCUCHA ESTE AUDIO:")
                    contenido_a_enviar.append(audio_blob)
                else:
                    contenido_a_enviar.append(f"LEE ESTE TEXTO:\n{transcripcion}")
                
                # Enviar todo a la IA
                respuesta = model.generate_content(contenido_a_enviar)
                texto_ia = respuesta.text
                
                contexto_datos = extraer_datos_ia(texto_ia)
                
                doc = DocxTemplate("plantilla.docx")
                doc.render(contexto_datos)
                
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                st.success("¡Informe generado a partir del audio con éxito!")
                
                st.download_button(
                    label="📥 Descargar Informe Final (Word)",
                    data=buffer,
                    file_name=f"Informe_{contexto_datos.get('nombre', 'Paciente')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"Error técnico: {e}")