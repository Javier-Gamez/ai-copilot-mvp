from core.conversation import ConversationSession

# Iniciamos sesión con límite de solo 2 turnos para probar rápido
session = ConversationSession(max_turns=2)

print("--- Turno 1: Comando /nota ---")
# Esto debería inyectar la instrucción de sistema oculta
resp1 = session.handle_input("/nota Comprar leche y pan")
print(f"Bot: {resp1['content']}")

print("\n--- Turno 2: Conversación normal ---")
resp2 = session.handle_input("¿Qué acabo de pedirte que anotes?")
print(f"Bot: {resp2['content']}")

print("\n--- Turno 3: Debería fallar por límite ---")
resp3 = session.handle_input("Hola, ¿sigues ahí?")
print(f"Bot: {resp3['content']}")