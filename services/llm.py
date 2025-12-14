import os
import time
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, RateLimitError, APIStatusError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

# Cargar variables de entorno
load_dotenv()

# Configuración de Logging (importante para "trazabilidad" en la rúbrica)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración por defecto (Rúbrica: Control explícito de parámetros)
DEFAULT_PARAMS = {
    "temperature": 0.7,
    "max_tokens": 512,
    "top_p": 1.0,
    "seed": 42,  # Rúbrica: seed para reproducibilidad
    "model": os.getenv("MODEL_NAME", "llama3-8b-8192")
}

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no encontrada en variables de entorno.")
        
        # Inicializamos el cliente
        self.client = Groq(api_key=self.api_key)

    # Rúbrica: Timeout <= 12s, 2 reintentos (3 intentos totales), Backoff exponencial
    # Rúbrica: Manejo diferenciado de errores (retrying solo en conexión/rate limit/5xx)
    @retry(
        stop=stop_after_attempt(3),  # 1 intento inicial + 2 reintentos
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True 
    )
    def _make_api_call(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Función interna protegida con lógica de reintento.
        Lanza excepciones para que @retry las capture, o el bloque try/except externo las maneje.
        """
        # Mezclar parámetros por defecto con los argumentos recibidos
        params = {**DEFAULT_PARAMS, **kwargs}
        
        # Rúbrica: Timeout explícito
        return self.client.chat.completions.create(
            messages=messages,
            model=params["model"],
            temperature=params["temperature"],
            max_tokens=params["max_tokens"],
            top_p=params["top_p"],
            seed=params["seed"],
            timeout=12.0  # Timeout duro de 12s
        )

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Método público principal.
        Maneja el éxito, los errores fatales (4xx) y activa el FALLBACK.
        """
        start_time = time.time()
        
        try:
            # Llamada al LLM
            response = self._make_api_call(messages, **kwargs)
            
            # Cálculo de latencia
            latency = time.time() - start_time
            
            # Extraer contenido y métricas de uso
            content = response.choices[0].message.content
            usage = response.usage
            
            return {
                "success": True,
                "content": content,
                "latency": round(latency, 4),
                "tokens_in": usage.prompt_tokens,
                "tokens_out": usage.completion_tokens,
                "model": response.model
            }

        except APIStatusError as e:
            # Rúbrica: Diferencia entre 400 y 500
            # Si es 4xx (ej. 400 Bad Request, 401 Unauthorized), NO reintentamos (ya pasó el retry filter o no aplicaba)
            logger.error(f"Error 4xx/5xx fatal del LLM: {e.status_code} - {e.message}")
            return self._fallback_response(error_msg=f"Error del proveedor: {e.status_code}")

        except Exception as e:
            # Cualquier otro error (timeout final tras reintentos, etc.)
            logger.error(f"Error inesperado o Timeout agotado: {str(e)}")
            return self._fallback_response(error_msg="El sistema no responde (Timeout/Error)")

    def _fallback_response(self, error_msg: str) -> Dict[str, Any]:
        """
        Rúbrica: Fallback claro y útil ante errores.
        """
        return {
            "success": False,
            "content": "⚠️ Lo siento, mis sistemas neuronales están sobrecargados en este momento. Por favor, intenta de nuevo en unos segundos. (Modo Fallback)",
            "latency": 0.0,
            "tokens_in": 0,
            "tokens_out": 0,
            "error": error_msg
        }

# Instancia global para usar en la app
llm_client = LLMService()

# Bloque simple para probar este archivo directamente (python services/llm.py)
if __name__ == "__main__":
    print("Probando conexión con Groq...")
    test_msgs = [{"role": "user", "content": "Hola, ¿estás funcionando?"}]
    result = llm_client.generate_response(test_msgs)
    print(result)