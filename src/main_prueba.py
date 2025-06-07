import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from chatbot.agent_agenda import date_parser_agent, translator_agent
from agents import Runner

result = Runner.run_sync(translator_agent, "Crea una tarea para mañana: comprar leche")
print(result.final_output)