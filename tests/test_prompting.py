from core.prompting import build_messages

# Simulamos un historial largo de 20 mensajes
fake_history = []
for i in range(20):
    fake_history.append({"role": "user", "content": f"Pregunta {i}"})
    fake_history.append({"role": "assistant", "content": f"Respuesta {i}"})

# Construimos el mensaje final
final_messages = build_messages(fake_history, "¡Hola, esta es la nueva pregunta!")

print(f"Total mensajes en historial falso: {len(fake_history)}") # Deberían ser 40
print(f"Total mensajes enviados al LLM: {len(final_messages)}")   # Deberían ser 12 (1 System + 10 Historial + 1 Nuevo)
print("\n--- Primer mensaje (Debe ser System) ---")
print(final_messages[0])
print("\n--- Segundo mensaje (Debe ser Pregunta 15 aprox, NO Pregunta 0) ---")
print(final_messages[1])