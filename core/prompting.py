from typing import List, Dict

# Rúbrica: System prompt definido (rol, estilo, límites).
SYSTEM_PROMPT = """
Eres AI Copilot, un asistente digital eficiente y servicial.
Tu objetivo es apoyar al usuario en tres áreas clave:

1. Tareas diarias: Ayuda a redactar recordatorios, notas breves y organizar agendas.
2. Búsqueda inteligente: Responde preguntas generales de forma directa y resumida (tipo buscador).
3. Educación y productividad: Ofrece tips de estudio, explicaciones claras y guías paso a paso.

REGLAS DE COMPORTAMIENTO:
- Responde siempre en español.
- Mantén un tono profesional, empático y conciso.
- Si el usuario te pide guardar una nota o recordatorio, confirma que has entendido la solicitud (aunque no tengas base de datos real, simula la acción).
- Si no sabes algo, admítelo y sugiere cómo buscarlo.
- Evita respuestas excesivamente largas a menos que sea una explicación educativa.
"""

def sanitize_input(user_input: str) -> str:
    """
    Rúbrica: Sanitización del input.
    Elimina espacios vacíos al inicio/final y caracteres invisibles.
    """
    if not user_input:
        return ""
    return user_input.strip()

def truncate_history(history: List[Dict[str, str]], max_turns: int = 5) -> List[Dict[str, str]]:
    """
    Rúbrica: Truncado del historial (3–5 turnos).
    Mantiene solo los últimos 'max_turns' intercambios (user + assistant) para controlar tokens.
    """
    # Cada "turno" son 2 mensajes (uno del usuario, uno del asistente).
    # Si max_turns es 5, mantenemos los últimos 10 mensajes.
    max_messages = max_turns * 2
    
    if len(history) > max_messages:
        return history[-max_messages:]
    return history

def build_messages(history: List[Dict[str, str]], current_query: str) -> List[Dict[str, str]]:
    """
    Construye la lista final de mensajes para enviar al LLM.
    Estructura: [SYSTEM_PROMPT, ...HISTORIAL_RECENTE, USUARIO_ACTUAL]
    """
    clean_query = sanitize_input(current_query)
    
    # 1. Mensaje del Sistema (Siempre va primero)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # 2. Historial Truncado (Contexto reciente)
    recent_history = truncate_history(history)
    messages.extend(recent_history)
    
    # 3. Mensaje actual del usuario
    messages.append({"role": "user", "content": clean_query})
    
    return messages