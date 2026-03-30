from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="openrouter/google/gemini-2.0-flash-001",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
    temperature=0.01
)
