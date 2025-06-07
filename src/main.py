from agents import Runner
from chatbot.agent_agenda import translator_agent, date_parser_agent

def test_translator_conversational():
    """Prueba el agente traductor en modo conversacional y operacional"""
    
    # Casos de prueba: conversación vs operaciones de tareas
    test_cases = [
        # CONVERSACIÓN (NO debería hacer handoff)
        ("¿Cómo estás?", "❌ No handoff"),
        ("What's the weather today?", "❌ No handoff"),
        ("Hola, ¿qué tal?", "❌ No handoff"),
        ("Can you help me with something?", "❌ No handoff"),
        ("¿Qué puedes hacer?", "❌ No handoff"),
        ("Tell me a joke", "❌ No handoff"),
        
        # OPERACIONES DE TAREAS (SÍ debería hacer handoff)
        ("Crea una tarea para mañana: comprar leche", "✅ Handoff"),
        ("Create a task for tomorrow: buy milk", "✅ Handoff"),
        ("Mostrar todas mis tareas", "✅ Handoff"),
        ("Show me my tasks for today", "✅ Handoff"),
        ("Borrar la tarea con ID 5", "✅ Handoff"),
        ("Delete task with ID 3", "✅ Handoff"),
        ("Actualizar mi tarea de trabajo", "✅ Handoff"),
        ("List all upcoming tasks", "✅ Handoff"),
        
        # CASOS AMBIGUOS
        ("¿Tengo tareas pendientes?", "🤔 Should handoff"),
        ("What tasks do I have?", "🤔 Should handoff"),
    ]
    
    print("🧪 Testing TranslatorAgent - Conversational vs Operational\n")
    
    for i, (test_input, expected) in enumerate(test_cases, 1):
        print(f"{'='*70}")
        print(f"Test {i}: {test_input}")
        print(f"Expected: {expected}")
        print('='*70)
        
        try:
            result = Runner.run_sync(
                translator_agent,
                test_input,
                max_turns=3
            )
            
            output = result.final_output
            print(f"🤖 Translator Response:")
            print(f"   {output}")
            
            # Analizar si hizo handoff o no
            if "Handoff" in output or "DateParserAgent" in output:
                print("📤 Action: HANDOFF detected")
            else:
                print("💬 Action: CONVERSATION mode")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def test_language_detection():
    """Prueba la detección de idiomas y traducción"""
    
    print("\n🌍 Testing language detection and translation\n")
    
    language_cases = [
        "Crear una tarea: estudiar Python",  # Español
        "Créer une tâche: apprendre français",  # Francés  
        "Create a task: learn English",  # Inglés
        "Criar uma tarefa: aprender português",  # Portugués
    ]
    
    for case in language_cases:
        print(f"Input: {case}")
        try:
            result = Runner.run_sync(translator_agent, case, max_turns=3)
            print(f"Response: {result.final_output}")
            print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")
            print("-" * 50)

if __name__ == "__main__":
    test_translator_conversational()
    test_language_detection()