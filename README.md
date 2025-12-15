# Javier de Jesús Gamez Rosas
# AI Copilot MVP
MVP de asistente virtual inteligente desarrollado en Python con **Llama 3.3** y **Streamlit**.
Diseñado para asistir en tareas diarias, búsqueda rápida y educación.

# Stack Tecnológico
* **Lenguaje:** Python 3.10+
* **LLM Provider:** Groq (Modelo: `llama-3.3-70b-versatile`).
    * *Justificación:* Se eligió Groq por su inferencia de ultra-baja latencia (<1s), esencial para una experiencia de chat fluida ("Búsqueda inteligente").
* **Interfaz:** Streamlit.
    * *Justificación:* Permite iteración rápida, manejo sencillo de estado (Session State) y visualización de métricas en tiempo real.
* **Robustez:** Librería `tenacity` para manejo de reintentos y backoff exponencial.

# Configuración del Modelo
Para cumplir con el control explícito de parámetros (ver `services/llm.py`):

* **Temperature:** `0.7` (Balance entre creatividad y coherencia).
* **Max Tokens:** `512` (Para respuestas concisas y control de costos).
* **Top P:** `1.0` (Muestreo estándar).
* **Timeout:** `12s` (Límite duro para evitar bloqueos).
* **Retries:** 2 reintentos con backoff exponencial (min 2s, max 10s).

# Lógica de Conversación

1.  **System Prompt:** Define al asistente como útil, empático y restringido a 3 áreas (Tareas, Búsqueda, Educación).
2.  **Memoria Corta:** Se implementó una ventana deslizante de **5 turnos** (User + Assistant) para mantener el contexto reciente sin desbordar la ventana de contexto.
3.  **Intents:** Detección de palabras clave al inicio (`/nota`, `/recordatorio`) para inyectar instrucciones de sistema específicas.
4.  **Sanitización:** Limpieza de espacios y caracteres invisibles en el input.

# Métricas de Desempeño (Promedio)
Medidas en entorno local (Windows) con conexión estándar:
* **Latencia p50:** ~0.4 - 0.8 segundos.
* **Tokens Salida:** ~50-150 por respuesta promedio.
* **Tasa de Fallos:** <1% (Manejo robusto de errores 4xx/5xx).

# Instalación y Uso
1.  Clonar repositorio:
    ```bash
    git clone <URL_DEL_REPO>
    ```
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configurar `.env` (ver `.env.example`).
4.  Ejecutar:
    ```bash
    streamlit run app/web.py
    ```

# Pruebas
Se incluyen 6 pruebas unitarias cubriendo truncado, intents y sanitización.
Ejecutar con: `pytest tests/`