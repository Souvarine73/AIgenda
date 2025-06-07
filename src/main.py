from agents import Runner
from chatbot.agent_agenda import translator_agent

import os
import sys
from agents import Runner, trace
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from chatbot.agent_agenda import translator_agent

def test_complete_workflow():
    """Prueba el flujo completo: Translator → DateParser → Database"""
    
    print("🧪 TESTING COMPLETE 3-AGENT WORKFLOW")
    print("="*60)
    
    # Test cases: diferentes idiomas y operaciones
    test_cases = [
        # ESPAÑOL - Crear tareas
        ("Crea una tarea para mañana: comprar leche", "🇪🇸 CREATE"),
        ("Crear tarea: estudiar Python para el lunes", "🇪🇸 CREATE"),
        
        # INGLÉS - Crear tareas  
        ("Create a task for tomorrow: buy milk", "🇺🇸 CREATE"),
        ("Add task: call doctor next week", "🇺🇸 CREATE"),
        
        # ESPAÑOL - Listar tareas
        ("Mostrar todas mis tareas", "🇪🇸 READ ALL"),
        ("¿Qué tareas tengo para hoy?", "🇪🇸 READ TODAY"),
        
        # INGLÉS - Listar tareas
        ("Show me all my tasks", "🇺🇸 READ ALL"), 
        ("What tasks do I have today?", "🇺🇸 READ TODAY"),
        
        # ESPAÑOL - Borrar
        ("Borrar la tarea con ID 1", "🇪🇸 DELETE"),
        
        # INGLÉS - Borrar
        ("Delete task with ID 2", "🇺🇸 DELETE"),
    ]
    
    for i, (query, description) in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i:2d}: {description}")
        print(f"Input:  {query}")
        print('='*60)
        
        try:
            # Ejecutar el flujo completo con tracing
            with trace(f"Test_{i:02d}_{description.replace(' ', '_')}", group_id="test_session"):
                result = Runner.run_sync(
                    translator_agent,
                    query,
                    max_turns=10  # Permitir múltiples handoffs
                )
            
            output = result.final_output
            print(f"✅ Output: {output}")
            
            # Analizar el resultado
            if "✅" in output:
                print("🎉 SUCCESS: Operation completed successfully")
            elif "❌" in output:
                print("⚠️  ERROR: Operation failed (expected for some tests)")
            elif "📭" in output:
                print("📭 EMPTY: No results found (normal for empty DB)")
            else:
                print("💬 CONVERSATION: Agent stayed in chat mode")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
        
        print("-" * 40)

def test_conversation_vs_operations():
    """Prueba que el agente distingue conversación de operaciones"""
    
    print("\n\n🤖 TESTING CONVERSATION vs TASK OPERATIONS")
    print("="*60)
    
    conversation_tests = [
        "¿Cómo estás?",
        "Hello, how are you?", 
        "What's the weather today?",
        "Tell me a joke",
        "¿Qué puedes hacer?"
    ]
    
    operation_tests = [
        "Crea una tarea: test",
        "Show my tasks",
        "Delete task 1",
        "List upcoming tasks"
    ]
    
    print("\n🔍 CONVERSATION MODE (should NOT handoff):")
    for i, query in enumerate(conversation_tests, 1):
        try:
            with trace(f"Conversation_Test_{i}", group_id="conversation_session"):
                result = Runner.run_sync(translator_agent, query, max_turns=3)
                output = result.final_output
            
            if any(word in output.lower() for word in ['handoff', 'dateparser', 'database']):
                print(f"❌ {query} → WRONG: Did handoff")
            else:
                print(f"✅ {query} → CORRECT: Stayed in conversation")
        except:
            print(f"❌ {query} → ERROR")
    
    print("\n🔧 OPERATION MODE (should handoff):")
    for i, query in enumerate(operation_tests, 1):
        try:
            with trace(f"Operation_Test_{i}", group_id="operation_session"):
                result = Runner.run_sync(translator_agent, query, max_turns=5)
                output = result.final_output
            
            if any(word in output for word in ['✅', '❌', '📭']) or 'task' in output.lower():
                print(f"✅ {query} → CORRECT: Executed operation")
            else:
                print(f"❌ {query} → WRONG: Stayed in conversation")
        except:
            print(f"❌ {query} → ERROR")

def test_database_operations():
    """Prueba operaciones específicas de base de datos"""
    
    print("\n\n💾 TESTING DATABASE OPERATIONS")
    print("="*60)
    
    # Test sequence: Create → Read → Delete
    sequence = [
        ("Create a task: Test task for today", "CREATE"),
        ("Show all my tasks", "READ ALL"),
        ("Get tasks for today", "READ TODAY"),  
        ("Delete task with ID 1", "DELETE"),
        ("Show all my tasks", "READ ALL (should be empty)"),
    ]
    
    with trace("Database_Operations_Sequence", group_id="db_test_session"):
        for i, (query, operation) in enumerate(sequence, 1):
            print(f"\n🔧 {operation}")
            print(f"Query: {query}")
            
            try:
                # Cada operación en una sub-traza
                with trace(f"DB_Step_{i}_{operation.replace(' ', '_')}"):
                    result = Runner.run_sync(translator_agent, query, max_turns=8)
                    print(f"Result: {result.final_output}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting tests at {datetime.now()}")
    print("Make sure you have:")
    print("1. ✅ OPENAI_API_KEY in your .env file")
    print("2. ✅ data/ directory exists")
    print("3. ✅ All prompt files created")
    print("4. 🔍 Traces will be visible in OpenAI Dashboard")
    print()
    
    # Run all tests with tracing
    with trace("Complete_Agent_Testing", group_id="main_test_session"):
        test_complete_workflow()
        test_conversation_vs_operations()
        test_database_operations()
    
    print(f"\n🏁 Tests completed at {datetime.now()}")
    print("🔍 Check your traces at: https://platform.openai.com/traces")