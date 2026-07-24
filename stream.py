# main.py
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessageChunk
from src.agent import agent_executor
from src.database import init_db

# Inicializamos la base de datos por primera vez antes de empezar.
init_db()

# Cargar variables de entorno (.env)
load_dotenv()

config = {"configurable": {
    "thread_id": "0001",
    "user_id": 1
    }
}

# Configuración estética de la app
st.set_page_config(
    page_title="Asistente Financiero", 
    page_icon="🗣️", 
    layout="centered"
)

# Título de la interfaz
st.title("🤖 Asistente Financiero Inteligente")
st.subheader("¿En qué puedo ayudarte hoy?")
st.write("Puedes consultar tu saldo, pedir un Bizum o preguntar por tus movimientos.")

# -----------------------------------------------------------------------------
# MANTENIMIENTO DEL HISTORIAL DE CONVERSACIÓN
# -----------------------------------------------------------------------------
# Inicializamos el historial en la sesión de Streamlit para que no se borre al recargar
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy tu asistente de Unicaja. ¿Qué deseas consultar hoy?"}
    ]

# Renderizar todos los mensajes guardados en el historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# -----------------------------------------------------------------------------
# FLUJO DE INTERACCIÓN EN TIEMPO REAL
# -----------------------------------------------------------------------------
# Capturar la entrada del usuario (caja de texto inferior) 
# Usamos el := walrus operator, que permite igualarlo a una función.
if prompt := st.chat_input("Escribe aquí tu consulta"):
    
    # 1. Mostrar inmediatamente el mensaje del usuario en la pantalla
    with st.chat_message("user"):
        st.write(prompt)
    
    # Guardarlo en el historial
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generar la respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            
            # --- CONEXIÓN CON TU BACKEND ---
            # Aquí es donde llamarás a la función de tu 'agent.py'
            # respuesta_ia = tu_funcion_del_agente(prompt)
            output_stream = agent_executor.stream(
                {"messages":[{"role":"user","content":prompt}]},
                config=config,
                stream_mode="messages"
            )

            contenedor_texto = st.empty()
            respuesta_ia = ""
            
            for chunk, metadata in output_stream:
                if isinstance(chunk, AIMessageChunk) and chunk.content and isinstance(chunk.content, str):
                    # 1. Acumulamos el contenido del token
                    respuesta_ia += chunk.content
                    # 2. Actualizamos el contenedor dinámicamente con un cursor visual "▌"
                    contenedor_texto.write(respuesta_ia + "▌")
            
            # Al terminar el bucle, pintamos el texto final sin el cursor
            contenedor_texto.write(respuesta_ia)
            
            # Guardar la respuesta definitiva en el historial
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})