from agents import Runner
from chatbot.agent_agenda import translator_agent, date_parser_agent

def test_date_parser():
    """Prueba el agente de fechas con diferentes casos"""
    
    # Casos de prueba típicos que recibirá del TranslatorAgent
    test_cases = [
        # Creación de tareas
        "Create a task for tomorrow: buy milk",
        "Create a task for next week: doctor appointment", 
        "Create a task for June 15th: birthday party",
        "Create a task in 3 days: call mom",
        
        # Consultas
        "Show me tasks for today",
        "Get all my tasks",
        "Show me upcoming tasks for next week",
        "Find task with ID 5",
        
        # Eliminación
        "Delete task with ID 3",
        
        # Sin fecha específica
        "Create a task: buy groceries",
    ]
    
    print("🧪 Testing DateParserAgent\n")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"{'='*60}")
        print(f"Test {i}: {test_input}")
        print('='*60)
        
        try:
            result = Runner.run_sync(
                date_parser_agent,
                test_input,
                max_turns=3
            )
            print(f"🤖 DateParser Output:")
            print(f"   {result.final_output}")
            
            # Verificar que el output tiene el formato esperado
            output = result.final_output
            if any(cmd in output for cmd in ["CREATE_TASK:", "GET_", "DELETE_TASK:"]):
                print("✅ Format: GOOD - Structured command detected")
            else:
                print("⚠️  Format: Check - May need adjustment")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()  # Línea en blanco para separar tests

def test_specific_dates():
    """Prueba casos específicos de fechas complicadas"""
    
    print("\n🗓️  Testing specific date scenarios\n")
    
    complex_cases = [
        "Create a task for this Friday: team meeting",
        "Create a task for the 25th: rent payment", 
        "Create a task for next Monday: project review",
        "Show me tasks for this month",
    ]
    
    for case in complex_cases:
        print(f"Input: {case}")
        try:
            result = Runner.run_sync(date_parser_agent, case, max_turns=2)
            print(f"Output: {result.final_output}")
            print("-" * 40)
        except Exception as e:
            print(f"Error: {e}")
            print("-" * 40)

if __name__ == "__main__":
    test_date_parser()