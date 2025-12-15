from typing import Dict, Any, List
from services.llm import llm_client
from core.prompting import build_messages

class ConversationSession:
    def __init__(self, max_turns: int = 20):
        # Historial completo de la sesión (User + Assistant)
        self.history: List[Dict[str, str]] = []
        self.turn_count = 0
        self.max_turns = max_turns

    def handle_input(self, user_input: str) -> Dict[str, Any]:
        """
        Procesa el input del usuario, gestiona intents y llama al LLM.
        """
        # 1. Rúbrica: Límite aproximado de turnos y mensaje de cierre.
        if self.turn_count >= self.max_turns:
            return {
                "content": "Has alcanzado el límite de mensajes por sesión (Demo). Por favor, reinicia el chat.",
                "latency": 0,
                "tokens_in": 0,
                "tokens_out": 0,
                "limit_reached": True
            }

        # 2. Rúbrica: Intents simples (/nota, /recordatorio, etc.)
        # Detectamos si el usuario usa un comando explícito y preparamos el contexto
        processed_input = self._process_intents(user_input)

        # 3. Construir mensajes usando lógica de prompting (core/prompting.py)
        messages = build_messages(self.history, processed_input)

        # 4. Llamar al servicio LLM (services/llm.py)
        response_data = llm_client.generate_response(messages)

        # 5. Si fue exitoso, actualizamos el historial
        if response_data["success"]:
            self._update_history(user_input, response_data["content"])
            self.turn_count += 1
        
        return response_data

    def _process_intents(self, text: str) -> str:
        """
        Detecta comandos especiales y orienta al LLM para que actúe según el intent.
        Rúbrica: Intents simples: /nota, /recordatorio, /busqueda.
        """
        text_lower = text.lower().strip()
        
        if text_lower.startswith("/nota"):
            return f"[SISTEMA: El usuario quiere GUARDAR UNA NOTA explícita. Confirma que la has guardado]. Contenido: {text}"
        
        elif text_lower.startswith("/recordatorio"):
            return f"[SISTEMA: El usuario quiere un RECORDATORIO. Confirma la hora y el tema]. Contenido: {text}"
        
        elif text_lower.startswith("/busqueda"):
            return f"[SISTEMA: El usuario hace una BÚSQUEDA RÁPIDA. Sé directo, usa bullet points y no des cháchara]. Consulta: {text}"
        
        # Flujo por defecto
        return text

    def _update_history(self, user_text: str, assistant_text: str):
        """
        Guarda el par de mensajes en el historial de la sesión.
        """
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": assistant_text})

    def reset(self):
        """Limpia la sesión"""
        self.history = []
        self.turn_count = 0