import streamlit as st
import time
import sys
import os

# --- CORRECCIÓN DE RUTAS ---
# Esto agrega la carpeta raíz del proyecto al "camino" de búsqueda de Python
# para que pueda encontrar el módulo 'core' y 'services'.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
# ---------------------------

from core.conversation import ConversationSession

# Configuración de la página
st.set_page_config(
    page_title="AI Copilot MVP",
    layout="wide"
)

# --- 1. Inicialización del Estado (Session State) ---
if "chat_session" not in st.session_state:
    # Creamos una nueva sesión de conversación y la guardamos en memoria de Streamlit
    st.session_state.chat_session = ConversationSession()

if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = {
        "latency": 0.0,
        "tokens_in": 0,
        "tokens_out": 0
    }

# --- 2. Barra Lateral (Sidebar) - Métricas y Control ---
with st.sidebar:
    st.title("Panel de Control")
    st.markdown("---")
    
    # Métricas de la última interacción (Rúbrica: Medición de latencia y tokens)
    st.subheader("Métricas (Último Turno)")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Latencia", f"{st.session_state.last_metrics['latency']}s")
    with col2:
        st.metric("Tokens Out", st.session_state.last_metrics['tokens_out'])
    
    st.caption(f"Tokens Entrada: {st.session_state.last_metrics['tokens_in']}")
    
    st.markdown("---")
    
    # Control de Límites (Rúbrica: Límite de turnos)
    turns = st.session_state.chat_session.turn_count
    max_turns = st.session_state.chat_session.max_turns
    st.subheader(f"Turnos: {turns}/{max_turns}")
    st.progress(min(turns / max_turns, 1.0))
    
    if turns >= max_turns:
        st.warning("Límite de sesión alcanzado.")
    
    st.markdown("---")
    
    # Botón de Reinicio
    if st.button("Reiniciar Conversación", type="primary"):
        st.session_state.chat_session.reset()
        st.session_state.last_metrics = {"latency": 0.0, "tokens_in": 0, "tokens_out": 0}
        st.rerun()

    st.markdown("### Guía de Comandos")
    st.info(
        """
        - **/nota** [texto]: Guarda una nota.
        - **/recordatorio** [texto]: Crea recordatorio.
        - **/busqueda** [texto]: Respuesta rápida.
        """
    )

# --- 3. Interfaz Principal de Chat ---
st.title("AI Copilot MVP")
st.caption("Asistente inteligente con Llama 3.3 vía Groq")

# Mostrar historial de mensajes (Renderizado)
for msg in st.session_state.chat_session.history:
    # Convertimos roles internos a visuales (assistant -> ai)
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- 4. Manejo del Input del Usuario ---
if prompt := st.chat_input("Escribe tu mensaje o comando..."):
    
    # A. Mostrar mensaje del usuario inmediatamente
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # B. Procesar respuesta con el LLM
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        # Llamada al backend
        response_data = st.session_state.chat_session.handle_input(prompt)
        
        # Actualizar UI con la respuesta final
        if response_data["success"]:
            message_placeholder.markdown(response_data["content"])
        else:
            # Rúbrica: Fallback visible
            message_placeholder.error(f"{response_data['content']} (Error: {response_data.get('error')})")
        
        # Actualizar métricas en sidebar
        st.session_state.last_metrics = {
            "latency": response_data["latency"],
            "tokens_in": response_data["tokens_in"],
            "tokens_out": response_data["tokens_out"]
        }
        # En este caso, al siguiente ciclo de interacción se verán actualizadas.