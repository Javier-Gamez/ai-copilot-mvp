import pytest
from core.prompting import truncate_history, sanitize_input, build_messages, SYSTEM_PROMPT
from core.conversation import ConversationSession

# --- BLOQUE 1: Pruebas de Prompting (3 Tests) ---

def test_sanitize_input():
    """Prueba que limpia espacios extra."""
    raw_text = "   Hola Mundo   "
    assert sanitize_input(raw_text) == "Hola Mundo"
    assert sanitize_input("") == ""

def test_truncate_history_limit():
    """Prueba que el historial no exceda el límite de turnos definidos."""
    # Creamos un historial falso de 20 mensajes (10 turnos)
    long_history = [{"role": "user", "content": str(i)} for i in range(20)]
    
    # Pedimos truncar a 2 turnos (4 mensajes)
    truncated = truncate_history(long_history, max_turns=2)
    
    assert len(truncated) == 4
    assert truncated[-1]["content"] == "19"  # Debe ser el último mensaje

def test_build_messages_structure():
    """Prueba que el System Prompt siempre sea el primero."""
    history = [{"role": "user", "content": "Hola"}]
    messages = build_messages(history, "Nueva pregunta")
    
    # El mensaje 0 debe ser System
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT
    # El último mensaje debe ser el del usuario actual
    assert messages[-1]["content"] == "Nueva pregunta"


# --- BLOQUE 2: Pruebas de Conversación (3 Tests) ---

def test_intent_detection_nota():
    """Prueba que detecta el comando /nota correctamente."""
    session = ConversationSession()
    processed = session._process_intents("/nota Comprar leche")
    
    assert "GUARDAR UNA NOTA" in processed
    assert "Comprar leche" in processed

def test_intent_detection_busqueda():
    """Prueba que detecta el comando /busqueda correctamente."""
    session = ConversationSession()
    processed = session._process_intents("/busqueda Capital de Francia")
    
    assert "BÚSQUEDA RÁPIDA" in processed

def test_conversation_turn_limit():
    """Prueba que bloquea la conversación al llegar al límite."""
    # Creamos sesión con límite de 1 turno
    session = ConversationSession(max_turns=1)
    
    # Forzamos el contador
    session.turn_count = 1
    
    # Intentamos enviar otro mensaje
    response = session.handle_input("¿Puedo hablar?")
    
    assert response["limit_reached"] is True
    assert "límite de mensajes" in response["content"]