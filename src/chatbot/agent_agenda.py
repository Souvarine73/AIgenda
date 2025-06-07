import os
from dotenv import load_dotenv
from agents import Agent, ModelSettings
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.operations import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    delete_task,
    get_tasks_for_today,
    get_upcoming_tasks
)

load_dotenv()

with open("src/chatbot/prompts/translator_prompt.txt", "r", encoding='utf-8') as f:
    TRANSLATOR_INSTRUCTIONS = f.read()

with open("src/chatbot/prompts/dateParser_prompt.txt", "r", encoding='utf-8') as f:
    DATEPARSER_INSTRUCTIONS = f.read()

with open("src/chatbot/prompts/database_prompt.txt", "r", encoding='utf-8') as f:
    DATABASE_INSTRUCTIONS = f.read()

tools = [
    create_task,
    get_all_tasks,
    get_task_by_id,
    delete_task,
    get_tasks_for_today,
    get_upcoming_tasks
    ]

database_agent = Agent(
    name="DatabaseAgent",
    instructions=DATABASE_INSTRUCTIONS,
    model="gpt-4o-mini",
    model_settings=ModelSettings(temperature=0.0, max_tokens=1000),
    tools=tools # type: ignore
)

date_parser_agent = Agent(
    name="DateParserAgent",
    instructions=DATEPARSER_INSTRUCTIONS + "\n\nCRITICAL OVERRIDE: Today is 2025-06-07. Tomorrow is 2025-06-08. Use ONLY 2025 dates.",
    model="gpt-4o-mini",
    model_settings=ModelSettings(temperature=0.0, max_tokens=1000),
    handoffs=[database_agent] 
)

translator_agent = Agent(
    name="TranslatorAgent",
    instructions=TRANSLATOR_INSTRUCTIONS,
    model="gpt-4o-mini",
    model_settings=ModelSettings(temperature=0.0, max_tokens=1000),
    handoffs=[date_parser_agent] 
)