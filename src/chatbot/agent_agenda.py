import os
from dotenv import load_dotenv
from agents import Agent, ModelSettings
import sys
from datetime import datetime

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
    DATEPARSER_INSTRUCTIONS = DATEPARSER_INSTRUCTIONS.format(
        current_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        today_date=datetime.now().strftime('%Y-%m-%d'),
        tomorrow_date=(datetime.now().replace(hour=9, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')),
        next_week_date=(datetime.now().strftime('%Y-%m-%d'))
    )

date_parser_agent = Agent(
    name="DateParserAgent",
    instructions=DATEPARSER_INSTRUCTIONS,
    model="gpt-4o-mini",
    model_settings=ModelSettings(temperature=0.0, max_tokens=1000),
    handoffs=[] #TODO: Add DatabaseAgent later
)

translator_agent = Agent(
    name="TranslatorAgent",
    instructions=TRANSLATOR_INSTRUCTIONS,
    model="gpt-4o-mini",
    model_settings=ModelSettings(temperature=0.0, max_tokens=1000),
    handoffs=[date_parser_agent] 
)